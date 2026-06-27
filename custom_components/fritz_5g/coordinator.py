from __future__ import annotations

import logging
import re
import xml.etree.ElementTree as ET

from datetime import timedelta

from fritzconnection import FritzConnection

from homeassistant.const import (
    CONF_HOST,
    CONF_USERNAME,
    CONF_PASSWORD,
)

from homeassistant.core import HomeAssistant
from homeassistant.helpers.update_coordinator import (
    DataUpdateCoordinator,
    UpdateFailed,
)

from .const import (
    DOMAIN,
    DEFAULT_SCAN_INTERVAL,
)

_LOGGER = logging.getLogger(__name__)


class Fritz5GCoordinator(DataUpdateCoordinator[dict]):
    """Coordinator für die FRITZ!Box 6860 5G."""

    def __init__(
        self,
        hass: HomeAssistant,
        config: dict,
    ) -> None:

        self._host = config[CONF_HOST]
        self._username = config[CONF_USERNAME]
        self._password = config[CONF_PASSWORD]

        super().__init__(
            hass,
            _LOGGER,
            name=DOMAIN,
            update_interval=timedelta(
                seconds=DEFAULT_SCAN_INTERVAL
            ),
        )
        
    async def _async_update_data(self) -> dict:
        """Liest die Daten der FRITZ!Box."""

        return await self.hass.async_add_executor_job(
            self._read_fritz_data
        )

    def _read_fritz_data(self) -> dict:
        """TR-064 GetInfoEx auslesen."""

        try:

            fc = FritzConnection(
                address=self._host,
                user=self._username,
                password=self._password,
            )

            info = fc.call_action(
                "X_AVM-DE_WANMobileConnection1",
                "GetInfoEx",
            )

            data: dict = {}

            data["technology"] = info.get(
                "NewCurrentAccessTechnology",
                ""
            )

            signal = info.get("NewSignalRSRP0", "")

            match = re.search(
                r"main=(-?\d+)",
                signal,
            )

            if match:
                data["lte_rsrp"] = int(match.group(1))

            xml = info.get("NewCellList", "")

            if xml:

                root = ET.fromstring(xml)

                for cell in root.findall("Cell"):

                    cell_type = cell.findtext(
                        "CellType",
                        "",
                    )

                    if cell_type == "lte":

                        self._parse_lte(
                            cell,
                            data,
                        )

                    elif cell_type == "nr5g":

                        self._parse_nr(
                            cell,
                            data,
                        )

            _LOGGER.debug(
                "FRITZ 5G Daten: %s",
                data,
            )

            return data

        except Exception as err:
            raise UpdateFailed(err) from err
            
    def _parse_lte(
        self,
        cell: ET.Element,
        data: dict,
    ) -> None:
        """LTE-Zelle auswerten."""

        rsrq = cell.findtext("Rsrq")
        if rsrq:
            data["lte_rsrq"] = int(rsrq)

        data["provider"] = cell.findtext(
            "Provider",
            "",
        )

        data["lte_cell_id"] = cell.findtext(
            "Cellid",
            "",
        )

    def _parse_nr(
        self,
        cell: ET.Element,
        data: dict,
    ) -> None:
        """5G-NR-Zelle auswerten."""

        rsrp = cell.findtext("RSRP")
        if rsrp:
            data["nr_rsrp"] = int(rsrp)

        rsrq = cell.findtext("Rsrq")
        if rsrq:
            data["nr_rsrq"] = int(rsrq)

        data["pci"] = cell.findtext(
            "PhysicalId",
            "",
        )

        data["distance"] = cell.findtext(
            "Distance",
            "",
        )

        data["nr_cell_id"] = cell.findtext(
            "Cellid",
            "",
        )
