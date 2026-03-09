"""
Neo4j Graph Risk Agent
Detects hidden relationships: shared directors, promoter cross-defaults,
and related-party risks using Neo4j graph database.
"""
import logging
from typing import Optional

logger = logging.getLogger(__name__)


class GraphAgent:
    """Neo4j-based director and company relationship risk detector."""

    def __init__(self, uri: str = "bolt://localhost:7687", user: str = "neo4j", password: str = "password"):
        self.uri = uri
        self.user = user
        self.password = password
        self._driver = None
        self._available = False
        self._init_driver()

    def _init_driver(self):
        try:
            from neo4j import GraphDatabase
            self._driver = GraphDatabase.driver(self.uri, auth=(self.user, self.password))
            # Test connection
            with self._driver.session() as session:
                session.run("RETURN 1")
            self._available = True
            logger.info("Neo4j connection established")
            self._ensure_constraints()
        except ImportError:
            logger.warning("neo4j driver not installed — graph agent disabled")
        except Exception as e:
            logger.warning(f"Neo4j not available: {e} — graph agent running in demo mode")

    def _ensure_constraints(self):
        """Create uniqueness constraints for nodes."""
        if not self._available:
            return
        try:
            with self._driver.session() as session:
                session.run("CREATE CONSTRAINT IF NOT EXISTS FOR (c:Company) REQUIRE c.name IS UNIQUE")
                session.run("CREATE CONSTRAINT IF NOT EXISTS FOR (d:Director) REQUIRE d.name IS UNIQUE")
        except Exception as e:
            logger.warning(f"Could not create Neo4j constraints: {e}")

    def add_company(self, company_name: str, industry: str = "", status: str = "Active"):
        """Add a company node to the graph."""
        if not self._available:
            return
        try:
            with self._driver.session() as session:
                session.run(
                    "MERGE (c:Company {name: $name}) SET c.industry = $industry, c.status = $status",
                    name=company_name, industry=industry, status=status,
                )
        except Exception as e:
            logger.warning(f"Neo4j add_company failed: {e}")

    def add_director(self, director_name: str, company_name: str, role: str = "Director"):
        """Add a director and their relationship to a company."""
        if not self._available:
            return
        try:
            with self._driver.session() as session:
                session.run("""
                    MERGE (d:Director {name: $director})
                    MERGE (c:Company {name: $company})
                    MERGE (d)-[:DIRECTOR_OF {role: $role}]->(c)
                """, director=director_name, company=company_name, role=role)
        except Exception as e:
            logger.warning(f"Neo4j add_director failed: {e}")

    def detect_cross_default_risk(self, company_name: str) -> dict:
        """
        Detect if any directors of this company are also directors
        of companies that defaulted / went bankrupt / are in NCLT.
        """
        if not self._available:
            return self._demo_result(company_name)

        try:
            with self._driver.session() as session:
                result = session.run("""
                    MATCH (target:Company {name: $company})<-[:DIRECTOR_OF]-(d:Director)
                    MATCH (d)-[:DIRECTOR_OF]->(other:Company)
                    WHERE other.name <> $company
                      AND other.status IN ['Defaulted', 'Bankrupt', 'NCLT', 'NPA']
                    RETURN d.name as director, collect(other.name) as risky_companies
                """, company=company_name)

                records = result.data()
                risk_connections = []
                for r in records:
                    risk_connections.append({
                        "director": r["director"],
                        "associated_risky_companies": r["risky_companies"],
                    })

                if risk_connections:
                    return {
                        "graph_risk_level": "High",
                        "graph_risk_summary": f"⚠️ {len(risk_connections)} director(s) of {company_name} are associated with defaulted/bankrupt companies.",
                        "risk_connections": risk_connections,
                        "graph_score": 70.0,
                    }
                else:
                    return {
                        "graph_risk_level": "Low",
                        "graph_risk_summary": f"✅ No cross-default director risks detected for {company_name}.",
                        "risk_connections": [],
                        "graph_score": 10.0,
                    }
        except Exception as e:
            logger.warning(f"Neo4j query failed: {e}")
            return self._demo_result(company_name)

    def find_related_companies(self, company_name: str, depth: int = 2) -> list[dict]:
        """Find companies connected via shared directors."""
        if not self._available:
            return []
        try:
            with self._driver.session() as session:
                result = session.run("""
                    MATCH (target:Company {name: $company})<-[:DIRECTOR_OF]-(d:Director)-[:DIRECTOR_OF]->(related:Company)
                    WHERE related.name <> $company
                    RETURN related.name as company, related.status as status, count(d) as shared_directors
                    ORDER BY shared_directors DESC
                    LIMIT 10
                """, company=company_name)
                return result.data()
        except Exception as e:
            logger.warning(f"Neo4j related companies query failed: {e}")
            return []

    def _demo_result(self, company_name: str) -> dict:
        """Return demo result when Neo4j is unavailable."""
        return {
            "graph_risk_level": "Low",
            "graph_risk_summary": "Neo4j not connected — graph risk analysis unavailable. Start Neo4j with: docker run -d -p 7474:7474 -p 7687:7687 -e NEO4J_AUTH=neo4j/password neo4j",
            "risk_connections": [],
            "graph_score": 20.0,
        }

    def close(self):
        if self._driver:
            self._driver.close()


# Singleton
graph_agent = GraphAgent()
