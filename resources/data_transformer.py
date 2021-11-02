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
ID_KEY = "id"
IP_KEY = "ip"
UNKNOWN_ENTITY = "unknown"

IP_TYPES = [ MACHINE_IP_KEY, INTERNAL_IP_KEY, SOURCE_IP_KEY]

# In some cases, audit entries can have multiple and different ip parameters
# We will try to resolve them to someone in the identity mapping
# If we fail to resolve, then dump it under an "unknown" entity
def get_offending_entity(entry, identity_mapping):
    entity_ip = UNKNOWN_ENTITY
    entity_id = UNKNOWN_ENTITY
    for ip_type in IP_TYPES:
        if entry.get(ip_type):
            entity_ip = entry.get(ip_type)
            entity_id = identity_mapping.get(entity_ip)
        if entity_id and entity_id != UNKNOWN_ENTITY:
            break
    return { ID_KEY: entity_id, IP_KEY: entity_ip }

def transform_raw_data(raw_data, incident_type, identity_mapping):
    output = {}
    for entry in raw_data:
        offending_entity = get_offending_entity(entry, identity_mapping)
        id = offending_entity[ID_KEY]
        ip = offending_entity[IP_KEY]
        if not (id in output):
            output[id] = AuditProfile(id)
        output[id].add_incident(incident_type, entry[PRIORITY_KEY], ip, entry[TIMESTAMP_KEY])
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
