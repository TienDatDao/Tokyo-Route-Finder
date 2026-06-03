"""
Graph Manager - Quản lý lifecycle của graph với incidents.

Kiến trúc:
    RAW DATA
        ↓
    BUILD FRESH GRAPH
        ↓
    APPLY INCIDENTS
        ↓
    SAVE CURRENT GRAPH

Không mutate original graph trong RAM.
Luôn rebuild graph mới từ raw data để tránh shared-state bug.
"""

import os
import json
import pickle

from typing import Optional, List, Dict, Any

from data_system.core.models import (
    Graph,
    Incident,
    IncidentType
)

from data_system.core.graph_builder import (
    build_tokyo_graph
)

from data_system.core.incident_manager import (
    apply_incidents
)


class GraphManager:

    def __init__(self, cache_dir: str):

        self.cache_dir = cache_dir

        self.original_graph_file = os.path.join(
            cache_dir,
            "graph_original.pkl"
        )

        self.current_graph_file = os.path.join(
            cache_dir,
            "graph_current.pkl"
        )

        self.incidents_file = os.path.join(
            cache_dir,
            "incidents.json"
        )

        self.graph_metadata_file = os.path.join(
            cache_dir,
            "graph_metadata.json"
        )

        # RAM cache
        self.original_graph: Optional[Graph] = None
        self.current_graph: Optional[Graph] = None
        self.current_incidents: List[Incident] = []
        
        # Raw data path (sẽ được set sau)
        self.raw_data_path: Optional[str] = None

        self._ensure_cache_dir()

        # Auto load original graph
        if os.path.exists(self.original_graph_file):
            self.load_original()
    
    def set_raw_data_path(self, raw_data_path: str):
        """Set đường dẫn đến raw data để auto-build graph nếu cần."""
        self.raw_data_path = raw_data_path

    # =========================================================
    # CACHE
    # =========================================================

    def _ensure_cache_dir(self):

        if not os.path.exists(self.cache_dir):
            os.makedirs(self.cache_dir)

    def _save_metadata(self, metadata: Dict[str, Any]):

        with open(
            self.graph_metadata_file,
            'w',
            encoding='utf-8'
        ) as f:

            json.dump(
                metadata,
                f,
                ensure_ascii=False,
                indent=2
            )

    # =========================================================
    # BUILD GRAPH
    # =========================================================

    def build_graph_from_raw(
        self,
        raw_dir: str
    ) -> Graph:
        """
        Build fresh graph từ raw data.
        """

        print(
            f"🔨 [GraphManager] Building graph from {raw_dir}..."
        )

        p_stations = os.path.join(
            raw_dir,
            "stations.json"
        )

        p_railway = os.path.join(
            raw_dir,
            "railway.json"
        )

        p_train_types = os.path.join(
            raw_dir,
            "train_types.json"
        )

        p_groups = os.path.join(
            raw_dir,
            "station_groups.json"
        )

        graph = build_tokyo_graph(
            p_stations,
            p_railway,
            p_train_types,
            p_groups
        )

        nodes = len(graph.nodes)

        edges = sum(
            len(edge_list)
            for edge_list in graph.edges.values()
        )

        print(
            f"✅ [GraphManager] Graph built: "
            f"{nodes} nodes, {edges} edges"
        )

        return graph

    def build_and_save_original(
        self,
        raw_dir: str
    ) -> Graph:
        """
        Build original graph và save cache.
        """

        graph = self.build_graph_from_raw(raw_dir)

        with open(self.original_graph_file, 'wb') as f:
            pickle.dump(graph, f)

        self.original_graph = graph

        nodes = len(graph.nodes)

        edges = sum(
            len(edge_list)
            for edge_list in graph.edges.values()
        )

        self._save_metadata({
            "status": "original_built",
            "original_nodes": nodes,
            "original_edges": edges
        })

        print(
            f"✅ [GraphManager] Original graph saved"
        )

        return graph

    # =========================================================
    # APPLY INCIDENTS
    # =========================================================

    def apply_and_save_incidents(
        self,
        incidents: List[Incident],
        raw_dir: str
    ) -> Dict[str, Any]:
        """
        Rebuild fresh graph rồi apply incidents.
        """

        print(
            f"🔧 [GraphManager] Applying "
            f"{len(incidents)} incidents..."
        )

        # =====================================================
        # BUILD FRESH GRAPH
        # =====================================================

        fresh_graph = self.build_graph_from_raw(raw_dir)

        # Save original cache nếu chưa có
        if not os.path.exists(self.original_graph_file):

            with open(self.original_graph_file, 'wb') as f:
                pickle.dump(fresh_graph, f)

            self.original_graph = fresh_graph

        # =====================================================
        # APPLY INCIDENTS
        # =====================================================

        current_graph = apply_incidents(
            fresh_graph,
            incidents
        )

        # =====================================================
        # VALIDATE
        # =====================================================

        errors = []

        if hasattr(current_graph, 'validate'):
            errors = current_graph.validate()

        # =====================================================
        # SAVE CURRENT GRAPH
        # =====================================================

        with open(self.current_graph_file, 'wb') as f:
            pickle.dump(current_graph, f)

        # =====================================================
        # SAVE INCIDENTS
        # =====================================================

        incidents_data = [
            {
                "incident_id": inc.incident_id,
                "type": inc.type.value,
                "target_id": inc.target_id
            }
            for inc in incidents
        ]

        with open(
            self.incidents_file,
            'w',
            encoding='utf-8'
        ) as f:

            json.dump(
                incidents_data,
                f,
                ensure_ascii=False,
                indent=2
            )

        # =====================================================
        # UPDATE RAM
        # =====================================================

        self.current_graph = current_graph
        self.current_incidents = incidents

        # =====================================================
        # STATS
        # =====================================================

        original_nodes = len(fresh_graph.nodes)

        original_edges = sum(
            len(edge_list)
            for edge_list in fresh_graph.edges.values()
        )

        current_nodes = len(current_graph.nodes)

        current_edges = sum(
            len(edge_list)
            for edge_list in current_graph.edges.values()
        )

        removed_nodes = (
            original_nodes - current_nodes
        )

        removed_edges = (
            original_edges - current_edges
        )

        # =====================================================
        # SAVE METADATA
        # =====================================================

        self._save_metadata({

            "status": "incidents_applied",

            "original_nodes": original_nodes,
            "original_edges": original_edges,

            "current_nodes": current_nodes,
            "current_edges": current_edges,

            "removed_nodes": removed_nodes,
            "removed_edges": removed_edges,

            "incidents_count": len(incidents),

            "validation_errors": errors
        })

        # =====================================================
        # RESULT
        # =====================================================

        result = {

            "status": "SUCCESS",

            "message":
                f"Applied {len(incidents)} incidents successfully",

            "original_nodes": original_nodes,
            "original_edges": original_edges,

            "current_nodes": current_nodes,
            "current_edges": current_edges,

            "removed_nodes": removed_nodes,
            "removed_edges": removed_edges,

            "incidents": incidents_data,

            "validation_errors": errors
        }

        print("✅ [GraphManager] Incidents applied:")

        print(
            f"   Original: {original_nodes} nodes, "
            f"{original_edges} edges"
        )

        print(
            f"   Current:  {current_nodes} nodes, "
            f"{current_edges} edges"
        )

        print(
            f"   Removed:  {removed_nodes} nodes, "
            f"{removed_edges} edges"
        )

        return result

    # =========================================================
    # RESET
    # =========================================================

    def reset_to_original(
        self,
        raw_dir: str
    ) -> Dict[str, Any]:
        """
        Rebuild original graph hoàn toàn từ raw data.
        """

        print(
            "🔄 [GraphManager] Resetting to original graph..."
        )

        # Build fresh original graph
        fresh_graph = self.build_graph_from_raw(raw_dir)

        # Save original graph
        with open(self.original_graph_file, 'wb') as f:
            pickle.dump(fresh_graph, f)

        # Remove current graph
        if os.path.exists(self.current_graph_file):
            os.remove(self.current_graph_file)

        # Remove incidents
        if os.path.exists(self.incidents_file):
            os.remove(self.incidents_file)

        # Update RAM
        self.original_graph = fresh_graph
        self.current_graph = None
        self.current_incidents = []

        nodes = len(fresh_graph.nodes)

        edges = sum(
            len(edge_list)
            for edge_list in fresh_graph.edges.values()
        )

        # Save metadata
        self._save_metadata({

            "status": "reset_to_original",

            "original_nodes": nodes,
            "original_edges": edges,

            "current_nodes": nodes,
            "current_edges": edges,

            "removed_nodes": 0,
            "removed_edges": 0
        })

        print(
            f"✅ [GraphManager] Reset complete: "
            f"{nodes} nodes, {edges} edges"
        )

        return {

            "status": "SUCCESS",

            "message": "Reset to original graph",

            "original_nodes": nodes,
            "original_edges": edges,

            "current_nodes": nodes,
            "current_edges": edges,

            "removed_nodes": 0,
            "removed_edges": 0,

            "incidents": [],

            "validation_errors": []
        }

    # =========================================================
    # GETTERS
    # =========================================================

    def get_original_graph(self) -> Graph:
        """
        Lấy original graph từ memory hoặc cache.
        Nếu chưa có, tự động build từ raw data nếu raw_data_path đã được set.
        """

        if self.original_graph is not None:
            return self.original_graph

        if os.path.exists(self.original_graph_file):
            with open(self.original_graph_file, 'rb') as f:
                self.original_graph = pickle.load(f)
            return self.original_graph

        # Auto-build từ raw data nếu có path
        if self.raw_data_path:
            print(
                f"⚠️  [GraphManager] Original graph not found in cache, "
                f"auto-building from {self.raw_data_path}..."
            )
            return self.build_and_save_original(self.raw_data_path)

        raise RuntimeError(
            "Original graph not found in cache and raw_data_path not set"
        )

    def get_current_graph(self) -> Graph:
        """
        Lấy current graph từ cache hoặc memory.
        Nếu có current graph (incidents applied), trả về nó.
        Nếu không có, trả về original graph.
        """

        if self.current_graph is not None:
            return self.current_graph

        if os.path.exists(self.current_graph_file):
            with open(self.current_graph_file, 'rb') as f:
                self.current_graph = pickle.load(f)
            return self.current_graph

        return self.get_original_graph()

    def get_current_incidents(self) -> List[Incident]:

        if self.current_incidents:
            return self.current_incidents

        if os.path.exists(self.incidents_file):

            with open(
                self.incidents_file,
                'r',
                encoding='utf-8'
            ) as f:

                incidents_data = json.load(f)

            incidents = []

            for inc_data in incidents_data:

                incident = Incident(
                    incident_id=inc_data["incident_id"],

                    type=IncidentType(
                        inc_data["type"]
                    ),

                    target_id=inc_data["target_id"]
                )

                incidents.append(incident)

            self.current_incidents = incidents

            return incidents

        return []

    # =========================================================
    # COMPARE
    # =========================================================

    def compare_graphs(self) -> Dict[str, Any]:

        original = self.get_original_graph()

        current = self.get_current_graph()

        original_nodes = len(original.nodes)

        current_nodes = len(current.nodes)

        original_edges = sum(
            len(edges)
            for edges in original.edges.values()
        )

        current_edges = sum(
            len(edges)
            for edges in current.edges.values()
        )

        incidents_data = [
            {
                "incident_id": inc.incident_id,
                "type": inc.type.value,
                "target_id": inc.target_id
            }
            for inc in self.get_current_incidents()
        ]

        return {

            "original": {
                "nodes": original_nodes,
                "edges": original_edges
            },

            "current": {
                "nodes": current_nodes,
                "edges": current_edges
            },

            "difference": {

                "nodes_removed":
                    original_nodes - current_nodes,

                "edges_removed":
                    original_edges - current_edges,

                "nodes_percentage":

                    round(
                        (
                            original_nodes
                            - current_nodes
                        )
                        / original_nodes * 100,
                        2
                    )

                    if original_nodes > 0 else 0,

                "edges_percentage":

                    round(
                        (
                            original_edges
                            - current_edges
                        )
                        / original_edges * 100,
                        2
                    )

                    if original_edges > 0 else 0
            },

            "incidents": incidents_data
        }

    # =========================================================
    # LOAD
    # =========================================================

    def load_original(self):

        if os.path.exists(self.original_graph_file):

            with open(self.original_graph_file, 'rb') as f:
                self.original_graph = pickle.load(f)

            print(
                f"✅ [GraphManager] Loaded original graph: "
                f"{len(self.original_graph.nodes)} nodes"
            )