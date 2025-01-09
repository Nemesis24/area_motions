import logging
from homeassistant import config_entries
import voluptuous as vol
from homeassistant.helpers import config_validation as cv, area_registry, entity_registry, device_registry
from homeassistant.core import callback, HomeAssistant
from .const import DOMAIN

_LOGGER = logging.getLogger(__name__)

class AreaMotionsConfigFlow(config_entries.ConfigFlow, domain=DOMAIN):
    VERSION = 1

    @staticmethod
    @callback
    def async_get_options_flow(config_entry):
        return AreaMotionsOptionsFlow(config_entry)

    async def async_step_user(self, user_input=None):
        # Configuration initiale
        if self._async_current_entries():
            return self.async_abort(reason="single_instance_allowed")

        motions_by_area = await self._async_get_motions_by_area()

        if user_input is not None:
            excluded = []
            for area_name, _ in motions_by_area.items():
                display_name = self._get_display_name(area_name)
                area_excluded = user_input.get(display_name, [])
                excluded.extend(area_excluded)

            _LOGGER.debug(f"Creating entry with excluded entities: {excluded}")

            return self.async_create_entry(
                title="Area Motions",
                data={
                    "excluded_entities": excluded,
                }
            )

        data_schema = {}
        for area_name, motions in motions_by_area.items():
            display_name = self._get_display_name(area_name)
            motion_dict = {motion["id"]: f"{motion['name']} ({motion['id']})"
                            for motion in motions}
            data_schema[vol.Optional(display_name,
                                     default=[])] = cv.multi_select(motion_dict)

        _LOGGER.debug(f"Showing form with data schema: {data_schema}")

        return self.async_show_form(
            step_id="user",
            data_schema=vol.Schema(data_schema),
        )

    def _get_display_name(self, area_name):
        if area_name.lower().startswith('area_'):
            return area_name[5:]
        return area_name

    async def _async_get_motions_by_area(self):
        area_reg = area_registry.async_get(self.hass)
        entity_reg = entity_registry.async_get(self.hass)
        device_reg = device_registry.async_get(self.hass)

        motions_by_area = {}

        for area in area_reg.async_list_areas():
            area_name = area.name
            motions_by_area[area_name] = []

        for entity in entity_reg.entities.values():
            if not entity.entity_id.startswith("binary_sensor.") or not (entity.entity_id.endswith("_motion_sensor") or entity.entity_id.endswith("_occupancy")):
                continue

            area_id = None
            if entity.area_id:
                area_id = entity.area_id
            elif entity.device_id:
                device = device_reg.async_get(entity.device_id)
                if device and device.area_id:
                    area_id = device.area_id

            if area_id:
                area = area_reg.async_get_area(area_id)
                if area:
                    area_name = area.name

                    if area_name not in motions_by_area:
                        motions_by_area[area_name] = []

                    friendly_name = entity.name or entity.original_name or entity.entity_id
                    motions_by_area[area_name].append({
                        "id": entity.entity_id,
                        "name": friendly_name
                    })
                    _LOGGER.debug(f"Motion {entity.entity_id} ({friendly_name}) added to area {area_name}")

        motions_by_area = {k: v for k, v in motions_by_area.items() if v}

        sorted_areas = {}
        for area_name in sorted(motions_by_area.keys()):
            sorted_areas[area_name] = sorted(motions_by_area[area_name],
                                             key=lambda x: x["name"].lower())

        _LOGGER.debug(f"Areas found with their motions: {sorted_areas}")
        return sorted_areas

class AreaMotionsOptionsFlow(config_entries.OptionsFlow):
    def __init__(self, config_entry):
        self.config_entry = config_entry

    async def async_step_init(self, user_input=None):
        motions_by_area = await self._async_get_motions_by_area()
        current_excluded = self.config_entry.data.get("excluded_entities", [])

        if user_input is not None:
            excluded = []
            for area_name, motions in motions_by_area.items():
                display_name = self._get_display_name(area_name)
                area_excluded = user_input.get(display_name, [])
                excluded.extend(area_excluded)

            _LOGGER.debug(f"Updating excluded entities from {current_excluded} to {excluded}")

            new_data = {
                **self.config_entry.data,
                "excluded_entities": excluded,
            }

            self.hass.config_entries.async_update_entry(self.config_entry, data=new_data)
            await self.hass.config_entries.async_reload(self.config_entry.entry_id)
            return self.async_create_entry(title="", data={})

        data_schema = {}
        for area_name, motions in motions_by_area.items():
            display_name = self._get_display_name(area_name)
            motion_dict = {motion["id"]: f"{motion['name']} ({motion['id']})"
                            for motion in motions}
            area_excluded = [motion for motion in current_excluded
                             if any(m["id"] == motion for m in motions)]
            data_schema[vol.Optional(display_name,
                                     default=area_excluded)] = cv.multi_select(motion_dict)

        _LOGGER.debug(f"Showing form with data schema: {data_schema}")

        return self.async_show_form(
            step_id="init",
            data_schema=vol.Schema(data_schema)
        )

    _async_get_motions_by_area = AreaMotionsConfigFlow._async_get_motions_by_area
    _get_display_name = AreaMotionsConfigFlow._get_display_name

DOMAIN = 'area_motions'

CONFIG_SCHEMA = vol.Schema({
    DOMAIN: vol.Schema({}),
})

async def async_setup(hass: HomeAssistant, config: dict) -> bool:
    return True