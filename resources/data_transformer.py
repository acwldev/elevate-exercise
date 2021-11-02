import copy

LOW_PRIORITY = 'low'
MEDIUM_PRIORITY = 'medium'
HIGH_PRIORITY = 'high'
CRITICAL_PRIORITY = 'critical'
COUNT_KEY = 'count'
INCIDENTS_KEY = 'incidents'
TYPE_KEY = 'type'
IDENTIFIER_KEY = 'identifier'
PRIORITY_KEY = 'priority'
SOURCE_IP_KEY = 'source_ip'
INTERNAL_IP_KEY = 'internal_ip'
MACHINE_IP_KEY = 'machine_ip'
TIMESTAMP_KEY = 'timestamp'
EMPLOYEE_ID_KEY = 'employee_id'
ID_KEY = "id"
IP_KEY = "ip"
UNKNOWN_ENTITY = "unknown"

IP_TYPES = [ IDENTIFIER_KEY, MACHINE_IP_KEY, INTERNAL_IP_KEY, SOURCE_IP_KEY]

# This is an attempt to resolve the entity_id from an audit entry. This is the strategy:
# If employee_id exist, then use it
# If identifier exist and is numeric, then use it
# Otherwise, attempt to map identifer or any of the ips in the identifiers API
# Ultimately, if no matches are found, map to "unknown"
def get_employee_id(entry, identity_mapping):
    entity_id = UNKNOWN_ENTITY
    if entry.get(EMPLOYEE_ID_KEY):
        entity_id = entry.get(EMPLOYEE_ID_KEY)
    elif str(entry.get(IDENTIFIER_KEY, "")).isnumeric():
        entitry_id = int(entry.get(IDENTIFIER_KEY))
    else:
        for ip_type in IP_TYPES:
            entity_ip = entry.get(ip_type)
            if entity_ip:
                entity_id = identity_mapping.get(entity_ip, UNKNOWN_ENTITY)
            if entity_id and entity_id != UNKNOWN_ENTITY:
                break
    return entity_id

def transform_raw_data(raw_data, incident_type, identity_mapping):
    output = {}
    for entry in raw_data:
        id = get_employee_id(entry, identity_mapping)
        if not (id in output):
            output[id] = AuditProfile(id)
        new_entry = entry.copy()
        new_entry[TYPE_KEY] = type
        output[id].add_incident(entry)
    return output


# Return an aggregated AuditProfile from provided list of AuditProfiles
# Note: Destroys the input
def aggregate_data(all_ids, audit_profiles_by_type_and_id):
    aggregated_data = {}
    for id in all_ids:
        audit_profiles_by_type = {}
        for incident_type, audit_profiles_by_id in audit_profiles_by_type_and_id.items():
            if id in audit_profiles_by_id:
                audit_profiles_by_type[incident_type] = audit_profiles_by_id[id]

        aggregate_profile = AuditProfile(id)
        aggregate_profile.transfer_incidents(audit_profiles_by_type.values())
        aggregated_data[str(id)] = aggregate_profile.data
    return aggregated_data

DEFAULT_PRIORITY_SUBPROFILE = {
    COUNT_KEY: 0,
    INCIDENTS_KEY: []
}

PRIORITIES = [LOW_PRIORITY, MEDIUM_PRIORITY, HIGH_PRIORITY, CRITICAL_PRIORITY]

class AuditProfile:

    def __init__(self, id):
        self.id = id
        self.data = {
            LOW_PRIORITY: copy.deepcopy(DEFAULT_PRIORITY_SUBPROFILE),
            MEDIUM_PRIORITY: copy.deepcopy(DEFAULT_PRIORITY_SUBPROFILE),
            HIGH_PRIORITY: copy.deepcopy(DEFAULT_PRIORITY_SUBPROFILE),
            CRITICAL_PRIORITY: copy.deepcopy(DEFAULT_PRIORITY_SUBPROFILE)
        }

    def __str__(self):
        return str(self.data)

    def add_incident(self, entry):
        subprofile = self.data.get(entry[PRIORITY_KEY])
        if subprofile:
            subprofile[INCIDENTS_KEY].append(entry)
            subprofile[COUNT_KEY] = len(subprofile[INCIDENTS_KEY])
        else:
            print("Unknown priority observed: " + priority)

    def get_incidents(self, priority):
        return self.data[priority][INCIDENTS_KEY]

    def has_incident(self, priority):
        return len(self.get_incidents(priority)) > 0

    def earliest_incident(self, priority):
        incidents = self.get_incidents(priority)
        if len(incidents) > 0:
            return incidents[0]
        else:
            return None

    def pop_earliest_incident(self, priority):
        incidents = self.get_incidents(priority)
        if len(incidents) > 0:
            self.data[priority][COUNT_KEY] = len(incidents) - 1
            return incidents.pop()

    # Transfers all incidents in the input AuditProfile to this AuditProfile in the order of ascending time
    def transfer_incidents(self, profiles):
        for priority in PRIORITIES:
            current_profiles = []
            for profile in profiles:
                if profile.has_incident(priority):
                    current_profiles.append(profile)

            while current_profiles:
                earliest_profile = None
                earliest_timestamp = None

                ### Look for earliest incident of priority level among all profiles that still have incidents at that priority.
                ### Then transfer this earliest incident over to this instance
                for profile in current_profiles:
                    local_timestamp = profile.earliest_incident(priority)[TIMESTAMP_KEY]
                    if (not earliest_timestamp) or earliest_timestamp > local_timestamp:
                        earliest_profile = profile
                        earliest_timestamp = local_timestamp

                incident = earliest_profile.pop_earliest_incident(priority)
                self.add_incident(incident)

                ### Weed out any profiles that no longer of incidents in this priority level
                tmp_profiles = []
                for profile in current_profiles:
                    if profile.has_incident(priority):
                        tmp_profiles.append(profile)
                current_profiles = tmp_profiles
