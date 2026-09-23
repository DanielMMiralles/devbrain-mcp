"""DevBrain Neuroplasticity Engine v1.0 — Motor de Plasticidad Sináptica
Inspirado en LTP/LTD, regla de Hebb y poda sináptica del sistema nervioso.

Este módulo implementa un motor de neuroplasticidad inspirado en principios biológicos:
- Regla de Hebb ("neurons that fire together wire together"): Co-activaciones fortalecen las conexiones.
- Potenciación a Largo Plazo (LTP): Fortalecimiento de sinapsis.
- Depresión a Largo Plazo (LTD): Decaimiento temporal de las conexiones menos usadas.
- Poda Sináptica: Eliminación de sinapsis muy débiles para optimizar la red.
"""
from __future__ import annotations
import sqlite3
import datetime
import secrets
import math
from pathlib import Path
import logging

logger = logging.getLogger(__name__)

W_MAX = 100.0

def generate_session_id() -> str:
    """Genera un identificador de sesión corto basado en la fecha y un sufijo aleatorio."""
    date_str = datetime.datetime.now().strftime('%Y%m%d')
    suffix = secrets.token_hex(2)
    return f"{date_str}-{suffix}"

class SynapticEngine:
    """Gestiona conexiones ponderadas (sinapsis) entre nodos de conocimiento en una base de datos SQLite."""

    def __init__(self, db_path: Path):
        """
        Inicializa el motor sináptico y crea las tablas necesarias.
        
        Args:
            db_path: Ruta a la base de datos SQLite.
        """
        self.db_path = db_path
        self._init_db()

    def _get_connection(self) -> sqlite3.Connection:
        """Devuelve una conexión SQLite configurada."""
        conn = sqlite3.connect(self.db_path, timeout=10.0)
        conn.row_factory = sqlite3.Row
        return conn

    def _init_db(self) -> None:
        """Crea las tablas e índices si no existen."""
        try:
            with self._get_connection() as conn:
                cursor = conn.cursor()
                cursor.executescript('''
                    CREATE TABLE IF NOT EXISTS synapses (
                        id INTEGER PRIMARY KEY AUTOINCREMENT,
                        source_key TEXT NOT NULL,
                        target_key TEXT NOT NULL,
                        weight REAL DEFAULT 1.0,
                        fire_count INTEGER DEFAULT 1,
                        last_fired TEXT,
                        created_at TEXT,
                        UNIQUE(source_key, target_key)
                    );

                    CREATE TABLE IF NOT EXISTS activations (
                        id INTEGER PRIMARY KEY AUTOINCREMENT,
                        node_key TEXT NOT NULL,
                        context_type TEXT,
                        session_id TEXT,
                        activated_at TEXT
                    );

                    CREATE INDEX IF NOT EXISTS idx_synapses_source ON synapses(source_key);
                    CREATE INDEX IF NOT EXISTS idx_synapses_weight ON synapses(weight DESC);
                    CREATE INDEX IF NOT EXISTS idx_activations_node ON activations(node_key);
                    CREATE INDEX IF NOT EXISTS idx_activations_session ON activations(session_id);
                ''')
                conn.commit()
        except sqlite3.Error as e:
            logger.error(f"Error al inicializar la base de datos: {e}")

    def record_activation(self, node_key: str, context_type: str = 'general', session_id: str = '') -> None:
        """
        Registra una activación e implementa la regla de Hebb fortaleciendo las sinapsis
        con otros nodos activados en la misma sesión.
        """
        if not session_id:
            session_id = generate_session_id()
            
        now = datetime.datetime.now().isoformat()
        
        try:
            with self._get_connection() as conn:
                cursor = conn.cursor()
                
                # Insertar activación
                cursor.execute(
                    "INSERT INTO activations (node_key, context_type, session_id, activated_at) VALUES (?, ?, ?, ?)",
                    (node_key, context_type, session_id, now)
                )
                
                # Obtener otros nodos de la misma sesión
                cursor.execute(
                    "SELECT DISTINCT node_key FROM activations WHERE session_id = ? AND node_key != ?",
                    (session_id, node_key)
                )
                other_nodes = [row['node_key'] for row in cursor.fetchall()]
                
                conn.commit()
                
            # Fortalecer sinapsis con nodos co-activados
            for other_node in other_nodes:
                self.strengthen_synapse(node_key, other_node, delta=1.0)
                
        except sqlite3.Error as e:
            logger.error(f"Error al registrar activación para {node_key}: {e}")

    def strengthen_synapse(self, source: str, target: str, delta: float = 1.0) -> float:
        """
        Implementa Potenciación a Largo Plazo (LTP). Crea o actualiza sinapsis bidireccionales.
        Retorna el nuevo peso.
        """
        new_weight = self._update_synapse_weight(source, target, delta)
        self._update_synapse_weight(target, source, delta)
        return new_weight

    def _update_synapse_weight(self, source: str, target: str, delta: float) -> float:
        """Helper para actualizar el peso en una dirección."""
        now = datetime.datetime.now().isoformat()
        try:
            with self._get_connection() as conn:
                cursor = conn.cursor()
                
                cursor.execute(
                    "SELECT weight, fire_count FROM synapses WHERE source_key = ? AND target_key = ?",
                    (source, target)
                )
                row = cursor.fetchone()
                
                if row:
                    w_old = row['weight']
                    fire_count = row['fire_count'] + 1
                    w_new = w_old + delta * (1 - (w_old / W_MAX))
                    w_new = min(w_new, W_MAX)
                    
                    cursor.execute(
                        """
                        UPDATE synapses 
                        SET weight = ?, fire_count = ?, last_fired = ?
                        WHERE source_key = ? AND target_key = ?
                        """,
                        (w_new, fire_count, now, source, target)
                    )
                else:
                    w_new = min(1.0 + delta * (1 - 1.0 / W_MAX), W_MAX)
                    cursor.execute(
                        """
                        INSERT INTO synapses (source_key, target_key, weight, fire_count, last_fired, created_at)
                        VALUES (?, ?, ?, ?, ?, ?)
                        """,
                        (source, target, w_new, 1, now, now)
                    )
                
                conn.commit()
                return w_new
        except sqlite3.Error as e:
            logger.error(f"Error al fortalecer sinapsis {source}->{target}: {e}")
            return 0.0

    def decay_synapses(self, half_life_days: float = 30.0) -> int:
        """
        Implementa Depresión a Largo Plazo (LTD).
        Decae el peso de todas las sinapsis basándose en el tiempo desde su último uso.
        Retorna la cantidad de sinapsis actualizadas.
        """
        now_dt = datetime.datetime.now()
        decayed_count = 0
        try:
            with self._get_connection() as conn:
                cursor = conn.cursor()
                cursor.execute("SELECT id, weight, last_fired FROM synapses")
                synapses = cursor.fetchall()
                
                for row in synapses:
                    synapse_id = row['id']
                    w = row['weight']
                    last_fired_str = row['last_fired']
                    
                    if not last_fired_str:
                        continue
                        
                    try:
                        last_fired_dt = datetime.datetime.fromisoformat(last_fired_str)
                        delta_days = (now_dt - last_fired_dt).total_seconds() / (24 * 3600)
                        
                        if delta_days > 0:
                            w_decayed = w * math.pow(2, -delta_days / half_life_days)
                            if w_decayed != w:
                                cursor.execute(
                                    "UPDATE synapses SET weight = ? WHERE id = ?",
                                    (w_decayed, synapse_id)
                                )
                                decayed_count += 1
                    except ValueError:
                        continue
                        
                conn.commit()
        except sqlite3.Error as e:
            logger.error(f"Error al decaer sinapsis: {e}")
            
        return decayed_count

    def prune_synapses(self, min_weight: float = 0.1) -> int:
        """
        Elimina sinapsis con peso menor a min_weight.
        Retorna la cantidad de sinapsis podadas.
        """
        try:
            with self._get_connection() as conn:
                cursor = conn.cursor()
                cursor.execute("DELETE FROM synapses WHERE weight < ?", (min_weight,))
                pruned = cursor.rowcount
                conn.commit()
                return pruned
        except sqlite3.Error as e:
            logger.error(f"Error al podar sinapsis: {e}")
            return 0

    def get_associated_nodes(self, node_key: str, limit: int = 5) -> list[dict]:
        """
        Obtiene los top-N nodos más fuertemente conectados a un nodo dado.
        """
        try:
            with self._get_connection() as conn:
                cursor = conn.cursor()
                cursor.execute(
                    """
                    SELECT target_key as key, weight, fire_count 
                    FROM synapses 
                    WHERE source_key = ? 
                    ORDER BY weight DESC 
                    LIMIT ?
                    """,
                    (node_key, limit)
                )
                return [dict(row) for row in cursor.fetchall()]
        except sqlite3.Error as e:
            logger.error(f"Error al obtener nodos asociados para {node_key}: {e}")
            return []

    def get_hot_paths(self, context_type: str | None = None, limit: int = 10) -> list[dict]:
        """
        Obtiene los caminos sinápticos más fuertes (globalmente o por contexto).
        """
        try:
            with self._get_connection() as conn:
                cursor = conn.cursor()
                
                if context_type:
                    query = """
                        SELECT s.source_key as source, s.target_key as target, s.weight, s.fire_count
                        FROM synapses s
                        JOIN activations a ON s.source_key = a.node_key
                        WHERE a.context_type = ?
                        GROUP BY s.source_key, s.target_key, s.weight, s.fire_count
                        ORDER BY s.weight DESC
                        LIMIT ?
                    """
                    cursor.execute(query, (context_type, limit))
                else:
                    query = """
                        SELECT source_key as source, target_key as target, weight, fire_count
                        FROM synapses
                        ORDER BY weight DESC
                        LIMIT ?
                    """
                    cursor.execute(query, (limit,))
                    
                return [dict(row) for row in cursor.fetchall()]
        except sqlite3.Error as e:
            logger.error(f"Error al obtener rutas calientes: {e}")
            return []

    def compute_synaptic_bonus(self, result_key: str, session_nodes: list[str], scale: float = 0.5) -> float:
        """
        Calcula el bonus sináptico para un resultado basado en sus conexiones 
        con los nodos recientemente activados en la sesión.
        """
        if not session_nodes:
            return 0.0
            
        bonus = 0.0
        try:
            with self._get_connection() as conn:
                cursor = conn.cursor()
                placeholders = ','.join('?' * len(session_nodes))
                
                # Buscar peso desde los nodos de la sesión hacia el resultado
                query = f"""
                    SELECT weight 
                    FROM synapses 
                    WHERE source_key IN ({placeholders}) AND target_key = ?
                """
                
                params = list(session_nodes)
                params.append(result_key)
                
                cursor.execute(query, params)
                rows = cursor.fetchall()
                
                for row in rows:
                    bonus += row['weight'] * scale
                    
            return bonus
        except sqlite3.Error as e:
            logger.error(f"Error al calcular bonus sináptico para {result_key}: {e}")
            return 0.0

    def get_session_nodes(self, session_id: str) -> list[str]:
        """Obtiene todos los node_keys activados en una sesión dada."""
        try:
            with self._get_connection() as conn:
                cursor = conn.cursor()
                cursor.execute(
                    "SELECT DISTINCT node_key FROM activations WHERE session_id = ?",
                    (session_id,)
                )
                return [row['node_key'] for row in cursor.fetchall()]
        except sqlite3.Error as e:
            logger.error(f"Error al obtener nodos para la sesión {session_id}: {e}")
            return []

    def get_stats(self) -> dict:
        """Obtiene estadísticas del motor de neuroplasticidad."""
        stats = {
            'total_synapses': 0,
            'total_activations': 0,
            'avg_weight': 0.0,
            'max_weight': 0.0,
            'strongest_path': None
        }
        
        try:
            with self._get_connection() as conn:
                cursor = conn.cursor()
                
                # Total de sinapsis, promedio y peso máximo
                cursor.execute("SELECT COUNT(*), AVG(weight), MAX(weight) FROM synapses")
                row = cursor.fetchone()
                if row and row[0]:
                    stats['total_synapses'] = row[0]
                    stats['avg_weight'] = row[1] if row[1] is not None else 0.0
                    stats['max_weight'] = row[2] if row[2] is not None else 0.0
                
                # Total de activaciones
                cursor.execute("SELECT COUNT(*) FROM activations")
                row = cursor.fetchone()
                if row:
                    stats['total_activations'] = row[0]
                    
                # Ruta más fuerte
                cursor.execute(
                    "SELECT source_key, target_key, weight FROM synapses ORDER BY weight DESC LIMIT 1"
                )
                strongest = cursor.fetchone()
                if strongest:
                    stats['strongest_path'] = (strongest['source_key'], strongest['target_key'], strongest['weight'])
                    
        except sqlite3.Error as e:
            logger.error(f"Error al obtener estadísticas: {e}")
            
        return stats
