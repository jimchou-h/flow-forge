"""Import smoke for Dify-aligned layer packages."""

import flow_forge.controllers
import flow_forge.core
import flow_forge.services


def test_layer_packages_import() -> None:
    assert flow_forge.controllers is not None
    assert flow_forge.services is not None
    assert flow_forge.core is not None
