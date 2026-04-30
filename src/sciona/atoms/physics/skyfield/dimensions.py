from __future__ import annotations

from sciona.ghost.dimensions import DIMENSIONLESS, METER, SECOND


LENGTH = METER
VELOCITY = METER.divide(SECOND)
ANGLE = DIMENSIONLESS
ANGULAR_RATE = SECOND.power(-1)

