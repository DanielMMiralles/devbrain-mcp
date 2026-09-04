import sys
import os
import argparse
from pathlib import Path

VAULT_DIR = Path(os.getenv("VAULT_DIR", r"C:\Users\damm1\OneDrive\Documentos\Obsidian Vault"))
SPECS_DIR = VAULT_DIR / "02-PROYECTOS" / "specs"

NESTJS_DTO = """import { IsString, IsNotEmpty, IsOptional } from 'class-validator';
import { ApiProperty } from '@nestjs/swagger';

export class Create{entity}Dto {
  @ApiProperty({ description: 'Nombre del recurso' })
  @IsString()
  @IsNotEmpty()
  name: string;

  @ApiProperty({ description: 'Descripcion detallada', required: false })
  @IsString()
  @IsOptional()
  description?: string;
}

export class Update{entity}Dto {
  @ApiProperty({ description: 'Nombre opcional para actualizar', required: false })
  @IsString()
  @IsOptional()
  name?: string;
}
"""

NESTJS_SVC = """import { Injectable, Logger } from '@nestjs/common';
import { Create{entity}Dto, Update{entity}Dto } from './dto/{kebab}.dto';

@Injectable()
export class {entity}Service {
  private readonly logger = new Logger('{entity}Service');

  async create(createDto: Create{entity}Dto) {
    this.logger.log(`Creando recurso: ${createDto.name}`);
    return {
      id: 'generated-uuid',
      ...createDto,
      createdAt: new Date().toISOString(),
    };
  }

  async findOne(id: string) {
    return { id, name: 'Sample {entity}', status: 'active' };
  }
}
"""

NESTJS_CTRL = """import { Controller, Get, Post, Body, Param } from '@nestjs/common';
import { ApiTags, ApiOperation, ApiResponse } from '@nestjs/swagger';
import { {entity}Service } from './{kebab}.service';
import { Create{entity}Dto } from './dto/{kebab}.dto';

@ApiTags('{kebab}')
@Controller('api/v1/{kebab}')
export class {entity}Controller {
  constructor(private readonly service: {entity}Service) {}

  @Post()
  @ApiOperation({ summary: 'Crear recurso conforme a spec BDD' })
  @ApiResponse({ status: 201, description: 'Recurso creado exitosamente' })
  async create(@Body() createDto: Create{entity}Dto) {
    return this.service.create(createDto);
  }

  @Get(':id')
  @ApiOperation({ summary: 'Obtener recurso por ID' })
  async findOne(@Param('id') id: string) {
    return this.service.findOne(id);
  }
}
"""

FASTAPI_ROUTER = """from fastapi import APIRouter, HTTPException, status
from pydantic import BaseModel, Field
from typing import Optional
from datetime import datetime

router = APIRouter(prefix="/api/v1/{kebab}", tags=["{kebab}"])

class {entity}Base(BaseModel):
    name: str = Field(..., min_length=2, description="Nombre del recurso")
    description: Optional[str] = Field(None, description="Descripcion")

class {entity}Create({entity}Base):
    pass

class {entity}Response({entity}Base):
    id: str
    created_at: datetime

    class Config:
        from_attributes = True

@router.post("/", response_model={entity}Response, status_code=status.HTTP_201_CREATED)
async def create_{py_name}(payload: {entity}Create):
    return {
        "id": "generated-uuid",
        "name": payload.name,
        "description": payload.description,
        "created_at": datetime.utcnow()
    }

@router.get("/{id}", response_model={entity}Response)
async def get_{py_name}(id: str):
    return {
        "id": id,
        "name": "Sample {entity}",
        "description": "Recuperado conforme a contrato BDD",
        "created_at": datetime.utcnow()
    }
"""

def generate_scaffold(spec_name: str, framework: str = "nestjs", output_dir: str = None):
    clean_kebab = spec_name.lower().replace(" ", "-").replace("spec-", "")
    entity_name = "".join(part.capitalize() for part in clean_kebab.split("-"))
    py_name = clean_kebab.replace("-", "_")

    if output_dir:
        out_base = Path(output_dir)
    else:
        out_base = SPECS_DIR / clean_kebab / "scaffold"

    out_base.mkdir(parents=True, exist_ok=True)

    if framework.lower() == "nestjs":
        dto_dir = out_base / "dto"
        dto_dir.mkdir(parents=True, exist_ok=True)

        dto_file = dto_dir / f"{clean_kebab}.dto.ts"
        svc_file = out_base / f"{clean_kebab}.service.ts"
        ctrl_file = out_base / f"{clean_kebab}.controller.ts"

        dto_file.write_text(NESTJS_DTO.replace("{entity}", entity_name).replace("{kebab}", clean_kebab), encoding="utf-8")
        svc_file.write_text(NESTJS_SVC.replace("{entity}", entity_name).replace("{kebab}", clean_kebab), encoding="utf-8")
        ctrl_file.write_text(NESTJS_CTRL.replace("{entity}", entity_name).replace("{kebab}", clean_kebab), encoding="utf-8")

        print(f"[OK] Scaffolding NestJS generado en: {out_base}")
        print(f"  -> {dto_file.name}")
        print(f"  -> {svc_file.name}")
        print(f"  -> {ctrl_file.name}")

    elif framework.lower() == "fastapi":
        router_file = out_base / f"{clean_kebab}_router.py"
        router_file.write_text(
            FASTAPI_ROUTER.replace("{entity}", entity_name).replace("{kebab}", clean_kebab).replace("{py_name}", py_name),
            encoding="utf-8"
        )
        print(f"[OK] Scaffolding FastAPI generado en: {router_file}")

if __name__ == "__main__":
    parser = argparse.ArgumentParser()
    parser.add_argument("spec", help="Nombre de la especificacion")
    parser.add_argument("--framework", choices=["nestjs", "fastapi"], default="nestjs")
    parser.add_argument("--out", help="Directorio de salida opcional")
    args = parser.parse_args()

    generate_scaffold(args.spec, args.framework, args.out)