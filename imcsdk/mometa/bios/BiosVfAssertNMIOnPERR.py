"""This module contains the general information for BiosVfAssertNMIOnPERR ManagedObject."""

from ...imcmo import ManagedObject
from ...imccoremeta import ImcVersion, MoPropertyMeta, MoMeta
from ...imcmeta import VersionMeta


class BiosVfAssertNMIOnPERRConsts():
    VP_ASSERT_NMION_PERR_DISABLED = "Disabled"
    VP_ASSERT_NMION_PERR_ENABLED = "Enabled"
    VP_ASSERT_NMION_PERR_DISABLED = "disabled"
    VP_ASSERT_NMION_PERR_ENABLED = "enabled"
    VP_ASSERT_NMION_PERR_PLATFORM_DEFAULT = "platform-default"


class BiosVfAssertNMIOnPERR(ManagedObject):
    """This is BiosVfAssertNMIOnPERR class."""

    consts = BiosVfAssertNMIOnPERRConsts()
    naming_props = set([])

    mo_meta = MoMeta("BiosVfAssertNMIOnPERR", "biosVfAssertNMIOnPERR", "Assert-NMI-on-PERR", VersionMeta.Version151f, "InputOutput", 0x1f, [], ["admin", "read-only", "user"], [u'biosPlatformDefaults', u'biosSettings'], [], ["Get", "Set"])

    prop_meta = {
        "child_action": MoPropertyMeta("child_action", "childAction", "string", VersionMeta.Version151f, MoPropertyMeta.INTERNAL, None, None, None, None, [], []), 
        "dn": MoPropertyMeta("dn", "dn", "string", VersionMeta.Version151f, MoPropertyMeta.READ_WRITE, 0x2, 0, 255, None, [], []), 
        "rn": MoPropertyMeta("rn", "rn", "string", VersionMeta.Version151f, MoPropertyMeta.READ_WRITE, 0x4, 0, 255, None, [], []), 
        "status": MoPropertyMeta("status", "status", "string", VersionMeta.Version151f, MoPropertyMeta.READ_WRITE, 0x8, None, None, None, ["", "created", "deleted", "modified", "removed"], []), 
        "vp_assert_nmi_on_perr": MoPropertyMeta("vp_assert_nmi_on_perr", "vpAssertNMIOnPERR", "string", VersionMeta.Version151f, MoPropertyMeta.READ_WRITE, 0x10, None, None, None, ["Disabled", "Enabled", "disabled", "enabled", "platform-default"], []), 
    }

    prop_map = {
        "childAction": "child_action", 
        "dn": "dn", 
        "rn": "rn", 
        "status": "status", 
        "vpAssertNMIOnPERR": "vp_assert_nmi_on_perr", 
    }

    def __init__(self, parent_mo_or_dn, **kwargs):
        self._dirty_mask = 0
        self.child_action = None
        self.status = None
        self.vp_assert_nmi_on_perr = None

        ManagedObject.__init__(self, "BiosVfAssertNMIOnPERR", parent_mo_or_dn, **kwargs)

