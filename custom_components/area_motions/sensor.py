import logging
from homeassistant.components.sensor import SensorEntity
from homeassistant.const import STATE_ON, STATE_OFF
from homeassistant.core import callback
from homeassistant.helpers import entity_registry, area_registry, device_registry
from .const import DOMAIN, ATTR_COUNT, ATTR_TOTAL

_LOGGER = logging.getLogger(__name__)

async def async_setup_entry(hass, entry, async_add_entities):
    excluded = entry.data.get("excluded_entities", [])
    
    _LOGGER.debug("Starting Area Motions configuration")
    _LOGGER.debug(f"Excluded entities: {excluded}")
    
    area_reg = area_registry.async_get(hass)
    entity_reg = entity_registry.async_get(hass)
    device_reg = device_registry.async_get(hass)
    
    areas = area_reg.async_list_areas()
    _LOGGER.debug(f"Found areas: {[area.name for area in areas]}")
    
    sensors = []
    all_motions = set()
    
    for area in areas:
        area_motions = set()
        area_excluded = set()
        
        for entity in entity_reg.entities.values():
            if entity.entity_id.startswith("binary_sensor.") and (entity.entity_id.endswith("_motion_sensor") or entity.entity_id.endswith("_occupancy")) and entity.area_id == area.id:
                if entity.entity_id not in excluded:
                    area_motions.add(entity.entity_id)
                    _LOGGER.debug(f"Motion {entity.entity_id} found directly in {area.name}")
                else:
                    area_excluded.add(entity.entity_id)
        
        for device_id in device_reg.devices:
            device = device_reg.async_get(device_id)
            if device and device.area_id == area.id:
                for entity in entity_reg.entities.values():
                    if entity.device_id == device_id and entity.entity_id.startswith("binary_sensor.") and (entity.entity_id.endswith("_motion_sensor") or entity.entity_id.endswith("_occupancy")):
                        if entity.entity_id not in excluded:
                            area_motions.add(entity.entity_id)
                            _LOGGER.debug(f"Motion {entity.entity_id} found via device in {area.name}")
                        else:
                            area_excluded.add(entity.entity_id)
        
        if area_motions:
            _LOGGER.debug(f"Area {area.name}: {len(area_motions)} motions found: {area_motions}")
            sensors.append(RoomMotionsSensor(area.name, list(area_motions), list(area_excluded)))
            all_motions.update(area_motions)
        else:
            # Supprimer l'entité de commutateur si la pièce n'a plus de capteurs motion
            sensor_motion_entity_id = f"sensor.motions_{area.name.lower().replace(' ', '_')}"
            entity = entity_reg.async_get(sensor_motion_entity_id)
            if entity:
                _LOGGER.debug(f"Removing switch entity for area with no motion sensors: {sensor_motion_entity_id}")
                entity_reg.async_remove(sensor_motion_entity_id)

    if all_motions:
        _LOGGER.debug(f"Total motions found: {len(all_motions)}")
        sensors.append(AllMotionsSensor(list(all_motions), excluded)) 
    
    _LOGGER.debug(f"Creating {len(sensors)} sensors")
    async_add_entities(sensors)

class RoomMotionsSensor(SensorEntity):
    def __init__(self, room_name, motions, excluded_motions):
        self._room = room_name
        self._motions = motions
        self._excluded_motions = excluded_motions
        self._attr_name = f"Motions {room_name}"
        self._attr_unique_id = f"area_motions_{room_name.lower().replace(' ', '_')}"
        self._state = STATE_OFF
        self._count = 0
        self._total = len(motions)
        self._motions_active = []
        self._motions_inactive = []
        _LOGGER.debug(f"Initializing sensor {self._attr_name} with {self._total} motions: {self._motions}")

    @property
    def state(self):
        return self._state

    @property
    def icon(self):
        return "mdi:motion-sensor" if self._state == STATE_ON else "mdi:motion-sensor-off"

    @property
    def extra_state_attributes(self):
        return {
            "count": self._count,
            "of": self._total,
            "count_of": f"{self._count}/{self._total}",
            "motions_active": self._motions_active,
            "motions_inactive": self._motions_inactive,
            "excluded_motions": self._excluded_motions,
        }

    async def async_added_to_hass(self):
        @callback
        def async_state_changed(*_):
            self.async_schedule_update_ha_state(True)

        for motion in self._motions:
            self.async_on_remove(
                self.hass.helpers.event.async_track_state_change_event(
                    motion, async_state_changed
                )
            )
        
        self.async_schedule_update_ha_state(True)

    async def async_update(self):
        self._count = 0
        self._motions_active = []
        self._motions_inactive = []
        
        for motion_id in self._motions:
            state = self.hass.states.get(motion_id)
            if state:
                if state.state == STATE_ON:
                    self._count += 1
                    self._motions_active.append(motion_id)
                else:
                    self._motions_inactive.append(motion_id)
        
        self._state = STATE_ON if self._count > 0 else STATE_OFF
        _LOGGER.debug(f"Updating {self._attr_name}: {self._count}/{self._total} motions active")

class AllMotionsSensor(RoomMotionsSensor):
    def __init__(self, motions, excluded_motions):
        super().__init__("All", motions, excluded_motions)
        self._attr_name = "All Area Motions"
        self._attr_unique_id = "area_motions_all"
