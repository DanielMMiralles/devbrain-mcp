"""
Tests Unitarios para TokenOptimizer (src/token_optimizer.py)
Verifica AST code slicing, chunking sináptico con token budget,
y deduplicación diferencial de sesiones.
"""
from __future__ import annotations
import unittest
import sys
from pathlib import Path

# Agregar src al path
SRC_DIR = Path(__file__).resolve().parent.parent / "src"
if str(SRC_DIR) not in sys.path:
    sys.path.insert(0, str(SRC_DIR))

from token_optimizer import TokenOptimizer, estimate_tokens


class TestTokenOptimizer(unittest.TestCase):

    def setUp(self):
        self.opt = TokenOptimizer()

    def test_estimate_tokens(self):
        self.assertEqual(estimate_tokens(""), 0)
        self.assertGreater(estimate_tokens("def hello_world(): pass"), 3)

    def test_ast_python_slicing(self):
        code = '''
"""Módulo de prueba para AST slicing"""

class UserManager:
    """Gestiona usuarios en el sistema."""
    def __init__(self, db):
        self.db = db
        self.cache = {}

    def get_user_by_id(self, user_id: int):
        """Retorna un usuario por su ID."""
        if user_id in self.cache:
            return self.cache[user_id]
        res = self.db.query("SELECT * FROM users WHERE id = ?", user_id)
        self.cache[user_id] = res
        return res

def helper_calculation(a: int, b: int) -> int:
    """Función auxiliar que calcula suma."""
    return a + b
'''
        res = self.opt.optimize_code_context(code, language="python", max_tokens=100)
        self.assertEqual(res["strategy"], "ast_slicing_python")
        self.assertGreater(res["savings_percent"], 0)
        self.assertIn("class UserManager", res["optimized_code"])
        self.assertIn("def get_user_by_id", res["optimized_code"])
        self.assertIn("def helper_calculation", res["optimized_code"])

    def test_ast_typescript_slicing(self):
        ts_code = '''
import { Injectable } from '@nestjs/common';

export interface UserDto {
    id: string;
    email: string;
}

export class AuthService {
    constructor(private readonly jwtService: JwtService) {}

    async validateUser(token: string): Promise<UserDto> {
        const decoded = await this.jwtService.verify(token);
        if (!decoded) {
            throw new Error('Unauthorized');
        }
        return decoded;
    }
}
'''
        res = self.opt.optimize_code_context(ts_code, language="typescript", max_tokens=100)
        self.assertEqual(res["strategy"], "ast_slicing_typescript")
        self.assertIn("interface UserDto", res["optimized_code"])
        self.assertIn("class AuthService", res["optimized_code"])
        self.assertIn("validateUser", res["optimized_code"])

    def test_knowledge_synaptic_chunking(self):
        markdown_text = '''# Guía de Arquitectura de Sistemas

## Introducción
Esta es una introducción breve a la arquitectura.

## Clean Architecture y Hexagonal
El núcleo de dominio no debe depender de bases de datos o frameworks.
Las entidades y casos de uso están en el centro, y los adaptadores afuera.
Esto permite desacoplar la lógica de negocio y realizar pruebas unitarias fácilmente.

## Docker y Contenedores
Los contenedores permiten empaquetar aplicaciones con sus dependencias.
Se utiliza Dockerfile para definir la imagen base y las capas de ejecución.

## Machine Learning & LLMs
Entrenamiento de modelos fundacionales y optimización de hiperparámetros.
'''
        # Búsqueda centrada en "clean architecture" con presupuesto estricto
        res = self.opt.optimize_knowledge_chunks(
            markdown_text,
            topic="clean architecture",
            max_tokens=50,
            active_session_synapses=["clean architecture", "hexagonal"]
        )
        self.assertGreaterEqual(res["chunks_kept"], 1)
        self.assertIn("Clean Architecture", res["optimized_text"])
        self.assertGreater(res["savings_percent"], 0)

    def test_session_deduplication(self):
        long_block = "A" * 600  # >120 caracteres para calificar como bloque
        session_id = "test-sess-dedup"

        # Primera vez: se registra pero no se deduplica
        r1 = self.opt.deduplicate_session_context(long_block, session_id=session_id)
        self.assertFalse(r1["was_deduplicated"])
        self.assertEqual(r1["deduplicated_text"], long_block)

        # Segunda vez: debe emitir el puntero
        r2 = self.opt.deduplicate_session_context(long_block, session_id=session_id)
        self.assertTrue(r2["was_deduplicated"])
        self.assertIn("📌", r2["deduplicated_text"])
        self.assertGreaterEqual(r2["savings_percent"], 70.0)

    def test_fallback_on_syntax_error(self):
        broken_python = "def invalid_syntax(:::"
        res = self.opt.optimize_code_context(broken_python, language="python", max_tokens=100)
        self.assertEqual(res["strategy"], "pass_through")
        self.assertEqual(res["optimized_code"], broken_python)


if __name__ == "__main__":
    unittest.main()
