from app.services.gtfs_loader import GTFSLoader
from typing import Dict, Optional
import logging

logger = logging.getLogger(__name__)

class TransitService:
    """
    Service layer for handling transit-related queries.
    
    Combines GTFS structured data with intelligent query routing
    to provide comprehensive transit information.
    """
    
    def __init__(self):
        self.gtfs = GTFSLoader()
        self.gtfs.load_data()
    
    def handle_query(self, location: str, query: str) -> Dict:
        """
        Route transit queries to appropriate handlers based on query type.
        
        Args:
            location: Location name or address
            query: Natural language transit query
            
        Returns:
            Dictionary with answer and supporting data
        """
        query_lower = query.lower()
        
        # Route based on query intent
        if any(word in query_lower for word in ["stop", "station"]):
            return self._handle_stop_query(location, query)
        elif any(word in query_lower for word in ["route", "line", "bus", "train"]):
            return self._handle_route_query(location, query)
        else:
            return self._handle_general_query(location, query)
    
    def _handle_stop_query(self, location: str, query: str) -> Dict:
        """Handle queries about stops and stations."""
        stops = self.gtfs.search_stops_by_name(location)
        
        if len(stops) == 0:
            return {
                "answer": f"No stops found matching '{location}'.",
                "data": None
            }
        
        # Format top results
        stop_list = stops.head(5)[['stop_name', 'stop_id', 'stop_lat', 'stop_lon']].to_dict('records')
        
        answer = f"Found {len(stops)} stops matching '{location}':\n\n"
        for stop in stop_list[:3]:
            answer += (
                f"- {stop['stop_name']} (ID: {stop['stop_id']})\n"
                f"  Location: ({stop['stop_lat']:.4f}, {stop['stop_lon']:.4f})\n\n"
            )
        
        return {
            "answer": answer.strip(),
            "data": stop_list
        }
    
    def _handle_route_query(self, location: str, query: str) -> Dict:
        """Handle queries about routes and lines."""
        routes = self.gtfs.get_all_routes()
        
        answer = f"MBTA operates {len(routes)} routes in the system.\n\n"
        answer += "Sample routes:\n"
        
        for _, route in routes.head(5).iterrows():
            route_name = route.get('route_long_name', 'N/A')
            route_short = route.get('route_short_name', '')
            answer += f"- {route_name}"
            if route_short:
                answer += f" ({route_short})"
            answer += "\n"
        
        return {
            "answer": answer.strip(),
            "data": routes.head(10).to_dict('records')
        }
    
    def _handle_general_query(self, location: str, query: str) -> Dict:
        """Handle general transit questions."""
        return {
            "answer": (
                f"General transit query for {location}: {query}\n\n"
                "For complex routing queries, consider integrating with "
                "MBTA's trip planning API or adding RAG-based reasoning."
            ),
            "data": None
        }