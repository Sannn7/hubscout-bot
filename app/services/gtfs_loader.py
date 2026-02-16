import pandas as pd
from pathlib import Path
from typing import Optional, List, Dict
import logging
from app.config import config

logger = logging.getLogger(__name__)

class GTFSLoader:
    """
    Loader for MBTA GTFS (General Transit Feed Specification) data.
    
    Handles loading and querying of transit data including:
    - Stops and stations
    - Routes and lines
    - Trips and schedules
    - Stop times
    """
    
    def __init__(self, gtfs_path: str = None):
        self.gtfs_path = Path(gtfs_path or config.GTFS_PATH)
        self.stops = None
        self.routes = None
        self.trips = None
        self.stop_times = None
        self._data_loaded = False
        
    def load_data(self) -> bool:
        """Load essential GTFS files into memory."""
        if self._data_loaded:
            logger.info("GTFS data already loaded")
            return True
        
        try:
            logger.info(f"Loading GTFS data from {self.gtfs_path}")
            
            # Load core files
            self.stops = pd.read_csv(self.gtfs_path / "stops.txt")
            self.routes = pd.read_csv(self.gtfs_path / "routes.txt")
            self.trips = pd.read_csv(self.gtfs_path / "trips.txt")
            
            # Note: stop_times.txt is ~123MB, load on-demand if needed
            
            logger.info(
                f"Loaded {len(self.stops)} stops, "
                f"{len(self.routes)} routes, "
                f"{len(self.trips)} trips"
            )
            
            self._data_loaded = True
            return True
            
        except Exception as e:
            logger.error(f"Error loading GTFS data: {e}")
            return False
    
    def get_stops_near_location(
        self, 
        lat: float, 
        lon: float, 
        radius_miles: float = 0.5
    ) -> pd.DataFrame:
        """
        Find stops within radius of a location.
        
        Uses approximate bounding box method. For production,
        consider using haversine distance or PostGIS.
        """
        if not self._data_loaded:
            self.load_data()
        
        # Approximate degrees per mile at Boston's latitude
        lat_range = radius_miles / 69.0
        lon_range = radius_miles / 54.6
        
        nearby = self.stops[
            (self.stops['stop_lat'].between(lat - lat_range, lat + lat_range)) &
            (self.stops['stop_lon'].between(lon - lon_range, lon + lon_range))
        ]
        
        return nearby
    
    def search_stops_by_name(self, query: str) -> pd.DataFrame:
        """Search stops by name (case-insensitive)."""
        if not self._data_loaded:
            self.load_data()
        
        return self.stops[
            self.stops['stop_name'].str.contains(query, case=False, na=False)
        ]
    
    def get_routes_at_stop(self, stop_id: str) -> List[Dict]:
        """Get all routes serving a specific stop."""
        if not self._data_loaded:
            self.load_data()
        
        # This requires joining stop_times -> trips -> routes
        # Simplified version returning all routes
        return self.routes.to_dict('records')
    
    def get_stop_info(self, stop_id: str) -> Optional[Dict]:
        """Get detailed information about a stop."""
        if not self._data_loaded:
            self.load_data()
        
        stop = self.stops[self.stops['stop_id'] == stop_id]
        
        if stop.empty:
            return None
        
        return stop.iloc[0].to_dict()
    
    def get_all_routes(self) -> pd.DataFrame:
        """Get all transit routes."""
        if not self._data_loaded:
            self.load_data()
        
        return self.routes