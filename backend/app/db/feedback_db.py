"""
SQLite Database for Feedback and Fine-Tuning System

Provides persistent storage for:
- User feedback (thumbs up/down, ratings)
- Training examples for fine-tuning
- Conversation history
- Fine-tuning job metadata
"""

import sqlite3
import json
from datetime import datetime
from pathlib import Path
from typing import Optional, List, Dict, Any
from contextlib import contextmanager


class FeedbackDatabase:
    """SQLite database for feedback and fine-tuning data"""
    
    def __init__(self, db_path: str = "data/feedback.db"):
        self.db_path = db_path
        
        # Create data directory if it doesn't exist
        Path(db_path).parent.mkdir(parents=True, exist_ok=True)
        
        # Initialize database
        self._init_db()
    
    @contextmanager
    def get_connection(self):
        """Context manager for database connections"""
        conn = sqlite3.connect(self.db_path)
        conn.row_factory = sqlite3.Row  # Return rows as dictionaries
        try:
            yield conn
            conn.commit()
        except Exception as e:
            conn.rollback()
            raise e
        finally:
            conn.close()
    
    def _init_db(self):
        """Initialize database schema"""
        with self.get_connection() as conn:
            cursor = conn.cursor()
            
            # Feedback table
            cursor.execute("""
                CREATE TABLE IF NOT EXISTS feedback (
                    id INTEGER PRIMARY KEY AUTOINCREMENT,
                    conversation_id TEXT NOT NULL,
                    message_id TEXT NOT NULL UNIQUE,
                    user_message TEXT NOT NULL,
                    agent_response TEXT NOT NULL,
                    agent_name TEXT NOT NULL,
                    feedback_type TEXT NOT NULL,
                    feedback_value TEXT NOT NULL,
                    comment TEXT,
                    metadata TEXT,
                    created_at TIMESTAMP DEFAULT CURRENT_TIMESTAMP,
                    updated_at TIMESTAMP DEFAULT CURRENT_TIMESTAMP
                )
            """)
            
            # Conversations table
            cursor.execute("""
                CREATE TABLE IF NOT EXISTS conversations (
                    id INTEGER PRIMARY KEY AUTOINCREMENT,
                    conversation_id TEXT NOT NULL UNIQUE,
                    user_id TEXT,
                    agent_name TEXT,
                    started_at TIMESTAMP DEFAULT CURRENT_TIMESTAMP,
                    last_message_at TIMESTAMP DEFAULT CURRENT_TIMESTAMP,
                    message_count INTEGER DEFAULT 0,
                    metadata TEXT
                )
            """)
            
            # Fine-tuning jobs table
            cursor.execute("""
                CREATE TABLE IF NOT EXISTS finetuning_jobs (
                    id INTEGER PRIMARY KEY AUTOINCREMENT,
                    job_id TEXT NOT NULL UNIQUE,
                    agent_name TEXT NOT NULL,
                    model TEXT NOT NULL,
                    status TEXT NOT NULL,
                    training_file_id TEXT,
                    fine_tuned_model TEXT,
                    hyperparameters TEXT,
                    training_examples_count INTEGER,
                    created_at TIMESTAMP DEFAULT CURRENT_TIMESTAMP,
                    started_at TIMESTAMP,
                    completed_at TIMESTAMP,
                    error TEXT,
                    metadata TEXT
                )
            """)
            
            # Training examples cache (for quick export)
            cursor.execute("""
                CREATE TABLE IF NOT EXISTS training_examples (
                    id INTEGER PRIMARY KEY AUTOINCREMENT,
                    feedback_id INTEGER NOT NULL,
                    agent_name TEXT NOT NULL,
                    system_prompt TEXT NOT NULL,
                    user_message TEXT NOT NULL,
                    assistant_response TEXT NOT NULL,
                    score INTEGER NOT NULL,
                    created_at TIMESTAMP DEFAULT CURRENT_TIMESTAMP,
                    FOREIGN KEY (feedback_id) REFERENCES feedback(id)
                )
            """)
            
            # Create indexes
            cursor.execute("""
                CREATE INDEX IF NOT EXISTS idx_feedback_conversation 
                ON feedback(conversation_id)
            """)
            cursor.execute("""
                CREATE INDEX IF NOT EXISTS idx_feedback_agent 
                ON feedback(agent_name)
            """)
            cursor.execute("""
                CREATE INDEX IF NOT EXISTS idx_feedback_type 
                ON feedback(feedback_type)
            """)
            cursor.execute("""
                CREATE INDEX IF NOT EXISTS idx_training_examples_agent 
                ON training_examples(agent_name)
            """)
            cursor.execute("""
                CREATE INDEX IF NOT EXISTS idx_training_examples_score 
                ON training_examples(score)
            """)
    
    def add_feedback(
        self,
        conversation_id: str,
        message_id: str,
        user_message: str,
        agent_response: str,
        agent_name: str,
        feedback_type: str,
        feedback_value: Any,
        comment: Optional[str] = None,
        metadata: Optional[Dict] = None
    ) -> int:
        """Add feedback entry"""
        with self.get_connection() as conn:
            cursor = conn.cursor()
            
            cursor.execute("""
                INSERT OR REPLACE INTO feedback (
                    conversation_id, message_id, user_message, agent_response,
                    agent_name, feedback_type, feedback_value, comment, metadata
                ) VALUES (?, ?, ?, ?, ?, ?, ?, ?, ?)
            """, (
                conversation_id,
                message_id,
                user_message,
                agent_response,
                agent_name,
                feedback_type,
                json.dumps(feedback_value),
                comment,
                json.dumps(metadata) if metadata else None
            ))
            
            return cursor.lastrowid
    
    def get_feedback(
        self,
        conversation_id: Optional[str] = None,
        agent_name: Optional[str] = None,
        feedback_type: Optional[str] = None,
        limit: Optional[int] = None
    ) -> List[Dict]:
        """Get feedback entries"""
        with self.get_connection() as conn:
            cursor = conn.cursor()
            
            query = "SELECT * FROM feedback WHERE 1=1"
            params = []
            
            if conversation_id:
                query += " AND conversation_id = ?"
                params.append(conversation_id)
            
            if agent_name:
                query += " AND agent_name = ?"
                params.append(agent_name)
            
            if feedback_type:
                query += " AND feedback_type = ?"
                params.append(feedback_type)
            
            query += " ORDER BY created_at DESC"
            
            if limit:
                query += " LIMIT ?"
                params.append(limit)
            
            cursor.execute(query, params)
            rows = cursor.fetchall()
            
            return [dict(row) for row in rows]
    
    def get_feedback_stats(self) -> Dict[str, Any]:
        """Get feedback statistics"""
        with self.get_connection() as conn:
            cursor = conn.cursor()
            
            # Total feedback
            cursor.execute("SELECT COUNT(*) FROM feedback")
            total = cursor.fetchone()[0]
            
            # By type
            cursor.execute("""
                SELECT feedback_type, COUNT(*) as count
                FROM feedback
                GROUP BY feedback_type
            """)
            by_type = {row[0]: row[1] for row in cursor.fetchall()}
            
            # By agent
            cursor.execute("""
                SELECT agent_name, COUNT(*) as count
                FROM feedback
                GROUP BY agent_name
            """)
            by_agent = {row[0]: row[1] for row in cursor.fetchall()}
            
            # Training examples
            cursor.execute("SELECT COUNT(*) FROM training_examples")
            training_examples = cursor.fetchone()[0]
            
            # High quality examples (score >= 4)
            cursor.execute("SELECT COUNT(*) FROM training_examples WHERE score >= 4")
            high_quality = cursor.fetchone()[0]
            
            return {
                "total_feedback": total,
                "by_type": by_type,
                "by_agent": by_agent,
                "training_examples": training_examples,
                "high_quality_examples": high_quality
            }
    
    def add_training_example(
        self,
        feedback_id: int,
        agent_name: str,
        system_prompt: str,
        user_message: str,
        assistant_response: str,
        score: int
    ) -> int:
        """Add training example"""
        with self.get_connection() as conn:
            cursor = conn.cursor()
            
            cursor.execute("""
                INSERT INTO training_examples (
                    feedback_id, agent_name, system_prompt,
                    user_message, assistant_response, score
                ) VALUES (?, ?, ?, ?, ?, ?)
            """, (
                feedback_id,
                agent_name,
                system_prompt,
                user_message,
                assistant_response,
                score
            ))
            
            return cursor.lastrowid
    
    def get_training_examples(
        self,
        agent_name: Optional[str] = None,
        min_score: int = 4,
        limit: Optional[int] = None
    ) -> List[Dict]:
        """Get training examples"""
        with self.get_connection() as conn:
            cursor = conn.cursor()
            
            query = """
                SELECT * FROM training_examples
                WHERE score >= ?
            """
            params = [min_score]
            
            if agent_name:
                query += " AND agent_name = ?"
                params.append(agent_name)
            
            query += " ORDER BY score DESC, created_at DESC"
            
            if limit:
                query += " LIMIT ?"
                params.append(limit)
            
            cursor.execute(query, params)
            rows = cursor.fetchall()
            
            return [dict(row) for row in rows]
    
    def add_finetuning_job(
        self,
        job_id: str,
        agent_name: str,
        model: str,
        status: str,
        training_examples_count: int,
        hyperparameters: Optional[Dict] = None,
        metadata: Optional[Dict] = None
    ) -> int:
        """Add fine-tuning job"""
        with self.get_connection() as conn:
            cursor = conn.cursor()
            
            cursor.execute("""
                INSERT INTO finetuning_jobs (
                    job_id, agent_name, model, status,
                    training_examples_count, hyperparameters, metadata
                ) VALUES (?, ?, ?, ?, ?, ?, ?)
            """, (
                job_id,
                agent_name,
                model,
                status,
                training_examples_count,
                json.dumps(hyperparameters) if hyperparameters else None,
                json.dumps(metadata) if metadata else None
            ))
            
            return cursor.lastrowid
    
    def update_finetuning_job(
        self,
        job_id: str,
        status: Optional[str] = None,
        fine_tuned_model: Optional[str] = None,
        error: Optional[str] = None,
        **kwargs
    ):
        """Update fine-tuning job"""
        with self.get_connection() as conn:
            cursor = conn.cursor()
            
            updates = []
            params = []
            
            if status:
                updates.append("status = ?")
                params.append(status)
                
                if status == "running":
                    updates.append("started_at = CURRENT_TIMESTAMP")
                elif status in ["succeeded", "failed", "cancelled"]:
                    updates.append("completed_at = CURRENT_TIMESTAMP")
            
            if fine_tuned_model:
                updates.append("fine_tuned_model = ?")
                params.append(fine_tuned_model)
            
            if error:
                updates.append("error = ?")
                params.append(error)
            
            if updates:
                query = f"UPDATE finetuning_jobs SET {', '.join(updates)} WHERE job_id = ?"
                params.append(job_id)
                cursor.execute(query, params)
    
    def get_finetuning_jobs(
        self,
        agent_name: Optional[str] = None,
        status: Optional[str] = None,
        limit: Optional[int] = None
    ) -> List[Dict]:
        """Get fine-tuning jobs"""
        with self.get_connection() as conn:
            cursor = conn.cursor()
            
            query = "SELECT * FROM finetuning_jobs WHERE 1=1"
            params = []
            
            if agent_name:
                query += " AND agent_name = ?"
                params.append(agent_name)
            
            if status:
                query += " AND status = ?"
                params.append(status)
            
            query += " ORDER BY created_at DESC"
            
            if limit:
                query += " LIMIT ?"
                params.append(limit)
            
            cursor.execute(query, params)
            rows = cursor.fetchall()
            
            return [dict(row) for row in rows]
    
    def clear_all(self):
        """Clear all data (for testing only)"""
        with self.get_connection() as conn:
            cursor = conn.cursor()
            cursor.execute("DELETE FROM feedback")
            cursor.execute("DELETE FROM training_examples")
            cursor.execute("DELETE FROM finetuning_jobs")
            cursor.execute("DELETE FROM conversations")


# Global database instance
feedback_db = FeedbackDatabase()
