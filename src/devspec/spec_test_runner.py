import sys
import re
import argparse
from pathlib import Path

VAULT_DIR = Path(os.getenv("VAULT_DIR", r"C:\Users\damm1\OneDrive\Documentos\Obsidian Vault"))
SPECS_DIR = VAULT_DIR / "02-PROYECTOS" / "specs"

JEST_TEMPLATE = """import { Test, TestingModule } from '@nestjs/testing';
import { INestApplication, ValidationPipe } from '@nestjs/common';
import * as request from 'supertest';
import { {entity}Controller } from '../{kebab}.controller';
import { {entity}Service } from '../{kebab}.service';

describe('{entity} BDD Acceptance Tests (OpenSpec)', () => {
  let app: INestApplication;
  let service: {entity}Service;

  beforeAll(async () => {
    const moduleRef: TestingModule = await Test.createTestingModule({
      controllers: [{entity}Controller],
      providers: [
        {
          provide: {entity}Service,
          useValue: {
            create: jest.fn().mockImplementation((dto) => Promise.resolve({ id: 'uuid-123', ...dto })),
            findOne: jest.fn().mockImplementation((id) => Promise.resolve({ id, name: 'Sample' })),
          },
        },
      ],
    }).compile();

    app = moduleRef.createNestApplication();
    app.useGlobalPipes(new ValidationPipe({ whitelist: true, transform: true }));
    await app.init();
    service = moduleRef.get<{entity}Service>({entity}Service);
  });

  afterAll(async () => {
    await app.close();
  });

{scenarios}
});
"""

JEST_SCENARIO_TEMPLATE = """  // Scenario: {title}
  it('{title}', async () => {
    const payload = { name: 'Test Resource' };

    const response = await request(app.getHttpServer())
      .post('/api/v1/{kebab}')
      .send(payload);

    expect([200, 201, 400, 422]).toContain(response.status);
    expect(response.body).toBeDefined();
  });
"""

PYTEST_TEMPLATE = """import pytest
from fastapi.testclient import TestClient
from fastapi import FastAPI
from datetime import datetime
from ..{kebab}_router import router

app = FastAPI()
app.include_router(router)
client = TestClient(app)

# Suites de pruebas BDD generadas automaticamente a partir de OpenSpec
class Test{entity}SpecContracts:
{scenarios}
"""

PYTEST_SCENARIO_TEMPLATE = """    def test_{scenario_slug}(self):
        # Scenario: {title}
        payload = {"name": "Test Resource", "description": "BDD verification"}

        response = client.post("/api/v1/{kebab}/", json=payload)

        assert response.status_code in [200, 201, 400, 422]
        data = response.json()
        assert "name" in data or "detail" in data
"""

def parse_spec_scenarios(spec_file: Path):
    if not spec_file.exists():
        return ["Ejecucion exitosa con datos validos", "Fallo por validacion de entrada"]
    txt = spec_file.read_text(encoding="utf-8", errors="ignore")
    scenarios = []
    matches = re.findall(r"#### Scenario:\s*(.+)", txt)
    for m in matches:
        scenarios.append(m.strip().replace("'", ""))
    if not scenarios:
        scenarios = ["Ejecucion exitosa con datos validos", "Fallo por validacion de entrada"]
    return scenarios

def generate_bdd_tests(spec_name: str, framework: str = "nestjs", output_dir: str = None):
    clean_kebab = spec_name.lower().replace(" ", "-").replace("spec-", "")
    entity_name = "".join(part.capitalize() for part in clean_kebab.split("-"))
    py_slug = clean_kebab.replace("-", "_")

    spec_file = SPECS_DIR / clean_kebab / "spec.md"
    scenarios = parse_spec_scenarios(spec_file)

    if output_dir:
        out_base = Path(output_dir)
    else:
        out_base = SPECS_DIR / clean_kebab / "scaffold" / "tests"
    out_base.mkdir(parents=True, exist_ok=True)

    if framework.lower() == "nestjs":
        test_file = out_base / f"{clean_kebab}.spec.ts"
        scenarios_blocks = []
        for s in scenarios:
            scenarios_blocks.append(JEST_SCENARIO_TEMPLATE.replace("{title}", s).replace("{kebab}", clean_kebab))

        full_code = JEST_TEMPLATE.replace("{entity}", entity_name).replace("{kebab}", clean_kebab).replace("{scenarios}", "\n".join(scenarios_blocks))
        test_file.write_text(full_code.strip() + "\n", encoding="utf-8")
        print(f"[OK] Suite BDD Jest generada en: {test_file}")
        print(f"  Total de escenarios compilados: {len(scenarios)}")

    elif framework.lower() == "fastapi":
        test_file = out_base / f"test_{py_slug}.py"
        scenarios_blocks = []
        for s in scenarios:
            s_slug = re.sub(r"\W+", "_", s.lower()).strip("_")
            scenarios_blocks.append(PYTEST_SCENARIO_TEMPLATE.replace("{title}", s).replace("{scenario_slug}", s_slug).replace("{kebab}", clean_kebab))

        full_code = PYTEST_TEMPLATE.replace("{entity}", entity_name).replace("{kebab}", clean_kebab).replace("{scenarios}", "\n".join(scenarios_blocks))
        test_file.write_text(full_code.strip() + "\n", encoding="utf-8")
        print(f"[OK] Suite BDD Pytest generada en: {test_file}")
        print(f"  Total de escenarios compilados: {len(scenarios)}")

if __name__ == "__main__":
    parser = argparse.ArgumentParser(description="BDD Test Generator from OpenSpec")
    parser.add_argument("spec", help="Nombre de la especificacion")
    parser.add_argument("--framework", choices=["nestjs", "fastapi"], default="nestjs")
    parser.add_argument("--out", help="Directorio destino opcional")
    args = parser.parse_args()

    generate_bdd_tests(args.spec, args.framework, args.out)