class SatelliteRadarServiceError(Exception):
    pass


class SatelliteRadarInvalidArgumentError(SatelliteRadarServiceError):
    pass


class SatelliteRadarCatalogUnavailableError(SatelliteRadarServiceError):
    pass


class SatelliteRadarCalculationError(SatelliteRadarServiceError):
    pass
