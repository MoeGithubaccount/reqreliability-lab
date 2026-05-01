"""
Baseline requirements dataset.
These are synthetic aerospace-style requirements written to be clear,
measurable, and verifiable - the starting point before mutation.
"""

REQUIREMENTS = [
    {
        "id": "REQ-001",
        "text": "The flight control system shall respond to pilot input within 200 milliseconds under all operating conditions.",
        "domain": "flight_control"
    },
    {
        "id": "REQ-002",
        "text": "The autopilot system shall disengage within 500 milliseconds upon detection of manual override activation.",
        "domain": "autopilot"
    },
    {
        "id": "REQ-003",
        "text": "The navigation display shall update position data at a minimum rate of 10 Hz during flight operations.",
        "domain": "navigation"
    },
    {
        "id": "REQ-004",
        "text": "The warning system shall activate an audible alert when cabin pressure drops below 75 kPa.",
        "domain": "safety"
    },
    {
        "id": "REQ-005",
        "text": "The data recorder shall store a minimum of 25 hours of flight data in non-volatile memory.",
        "domain": "data_management"
    },
    {
        "id": "REQ-006",
        "text": "The landing gear system shall fully extend or retract within 10 seconds of receiving the control signal.",
        "domain": "landing_gear"
    },
    {
        "id": "REQ-007",
        "text": "The engine monitoring system shall log temperature, pressure, and RPM values every 100 milliseconds.",
        "domain": "engine"
    },
    {
        "id": "REQ-008",
        "text": "The communication system shall maintain encrypted radio contact with ground control throughout the mission.",
        "domain": "communication"
    },
    {
        "id": "REQ-009",
        "text": "The fuel management system shall alert the crew when remaining fuel drops below 15 percent of total capacity.",
        "domain": "fuel"
    },
    {
        "id": "REQ-010",
        "text": "The collision avoidance system shall issue a resolution advisory within 35 seconds of detecting a traffic conflict.",
        "domain": "safety"
    },
]
