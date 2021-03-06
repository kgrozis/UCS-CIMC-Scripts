"""This module contains the general information for BiosVfOutOfBandMgmtPort ManagedObject."""

from ...imcmo import ManagedObject
from ...imccoremeta import ImcVersion, MoPropertyMeta, MoMeta
from ...imcmeta import VersionMeta


class BiosVfOutOfBandMgmtPortConsts():
    VP_OUT_OF_BAND_MGMT_PORT_DISABLED = "Disabled"
    VP_OUT_OF_BAND_MGMT_PORT_ENABLED = "Enabled"
    VP_OUT_OF_BAND_MGMT_PORT_DISABLED = "disabled"
    VP_OUT_OF_BAND_MGMT_PORT_ENABLED = "enabled"
    VP_OUT_OF_BAND_MGMT_PORT_PLATFORM_DEFAULT = "platform-default"


class BiosVfOutOfBandMgmtPort(ManagedObject):
    """This is BiosVfOutOfBandMgmtPort class."""

    consts = BiosVfOutOfBandMgmtPortConsts()
    naming_props = set([])

    mo_meta = MoMeta("BiosVfOutOfBandMgmtPort", "biosVfOutOfBandMgmtPort", "OoB-MgmtPort", VersionMeta.Version154, "InputOutput", 0x1f, [], ["admin"], [u'biosPlatformDefaults', u'biosSettings'], [], ["Get", "Set"])

    prop_meta = {
        "dn": MoPropertyMeta("dn", "dn", "string", VersionMeta.Version154, MoPropertyMeta.READ_WRITE, 0x2, 0, 255, None, [], []), 
        "rn": MoPropertyMeta("rn", "rn", "string", VersionMeta.Version154, MoPropertyMeta.READ_WRITE, 0x4, 0, 255, None, [], []), 
        "status": MoPropertyMeta("status", "status", "string", VersionMeta.Version154, MoPropertyMeta.READ_WRITE, 0x8, None, None, None, ["", "created", "deleted", "modified", "removed"], []), 
        "vp_out_of_band_mgmt_port": MoPropertyMeta("vp_out_of_band_mgmt_port", "vpOutOfBandMgmtPort", "string", VersionMeta.Version154, MoPropertyMeta.READ_WRITE, 0x10, None, None, None, ["Disabled", "Enabled", "disabled", "enabled", "platform-default"], []), 
    }

    prop_map = {
        "dn": "dn", 
        "rn": "rn", 
        "status": "status", 
        "vpOutOfBandMgmtPort": "vp_out_of_band_mgmt_port", 
    }

    def __init__(self, parent_mo_or_dn, **kwargs):
        self._dirty_mask = 0
        self.status = None
        self.vp_out_of_band_mgmt_port = None

        ManagedObject.__init__(self, "BiosVfOutOfBandMgmtPort", parent_mo_or_dn, **kwargs)

