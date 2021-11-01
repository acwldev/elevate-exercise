LOW_PRIORITY = 'low'
MEDIUM_PRIORITY = 'medium'
HIGH_PRIORITY = 'high'
CRITICAL_PRIORITY = 'critical'
COUNT_KEY = 'count'
INCIDENTS_KEY = 'incidents'
TYPE_KEY = 'type'
PRIORITY_KEY = 'priority'
SOURCE_IP_KEY = 'source_ip'
INTERNAL_IP_KEY = 'internal_ip'
MACHINE_IP_KEY = 'machine_ip'
TIMESTAMP_KEY = 'timestamp'
UNKNOWN_ENTITY = "unknown_entity"

def get_offending_entity(entry):
    return entry.get(MACHINE_IP_KEY) or entry.get(INTERNAL_IP_KEY) or entry.get(SOURCE_IP_KEY)

def transform_raw_data(raw_data, incident_type, identity_mapping):
    output = {}
    for entry in raw_data:
        offending_entity = get_offending_entity(entry)
        id = str(identity_mapping.get(offending_entity, UNKNOWN_ENTITY))
        if not (id in output):
            output[id] = AuditProfile(id)
        output[id].add_incident(incident_type, entry[PRIORITY_KEY], offending_entity, entry[TIMESTAMP_KEY])
    return output

def aggreagate_data(transformed_data):
    return transformed_data

DEFAULT_PRIORITY_SUBPROFILE = {
    COUNT_KEY: 0,
    INCIDENTS_KEY: []
}

class AuditProfile:

    def __init__(self, id):
        self.id = id
        self.data = {
            LOW_PRIORITY: DEFAULT_PRIORITY_SUBPROFILE.copy(),
            MEDIUM_PRIORITY: DEFAULT_PRIORITY_SUBPROFILE.copy(),
            HIGH_PRIORITY: DEFAULT_PRIORITY_SUBPROFILE.copy(),
            CRITICAL_PRIORITY: DEFAULT_PRIORITY_SUBPROFILE.copy()
        }

    def add_incident(self, type, priority, ip, timestamp):
        subprofile = self.data.get(priority)
        if subprofile:
            subprofile[INCIDENTS_KEY].append({
                TYPE_KEY: type,
                PRIORITY_KEY: priority,
                MACHINE_IP_KEY: ip,
                TIMESTAMP_KEY: timestamp
            })
            subprofile[COUNT_KEY] = len(subprofile[INCIDENTS_KEY])
        else:
            print("Unknown priority observed: " + priority)
