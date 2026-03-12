"""
PyLabRobot + Opentrons OT-2: basic liquid handling example for Monomer hackathon participants.

Demonstrates: setup deck, pick up tips, aspirate/dispense (with mixing), return tips.
Transfer flow: 24-well plate → 96-well deep → 96-well flat. Uses both tip types
(P300 left/channel 0, P1000 right/channel 1). Mixing is done by passing
mix=[Mix(volume_µL, repetitions, flow_rate_µL/s)] to aspirate() and/or dispense().

Deck layout (slots):
  Slot 1: 24-well deepwell plate, 10 mL (source)
  Slot 2: 96-well deepwell plate, 2.2 mL (intermediate)
  Slot 3: 96-well flat bottom plate, 360 µL (destination)
  Slot 6: 300 µL tip rack (P300 / channel 0)
  Slot 9: 1000 µL tip rack (P1000 / channel 1)

IMPORTANT: On the OT-2 dual pipette, pass use_channels=[0] for left (P300) or
use_channels=[1] for right (P1000). Tip rack and pipette must match.
"""
import asyncio
import os
from pylabrobot.liquid_handling import LiquidHandler, OpentronsOT2Backend
from pylabrobot.liquid_handling.standard import Mix
from pylabrobot.resources import (
    OTDeck,
    Cor_96_wellplate_360ul_Fb,
    Cor_Axy_24_wellplate_10mL_Vb,
    NEST_96_wellplate_2200uL_Ub,
)
from pylabrobot.resources.opentrons.load import load_ot_tip_rack

# -----------------------------------------------------------------------------
# Deck setup
# -----------------------------------------------------------------------------
OT2_HOST = os.environ.get("OT2_HOST")
if not OT2_HOST:
    raise ValueError(
        "OT2_HOST environment variable is not set. "
        "Set it to your robot's IP, e.g. in the terminal: export OT2_HOST=192.168.1.1"
    )
deck = OTDeck()
backend = OpentronsOT2Backend(host=OT2_HOST)
lh = LiquidHandler(backend=backend, deck=deck)

tip_300 = load_ot_tip_rack("opentrons_96_tiprack_300ul", "300uL")
tip_1000 = load_ot_tip_rack("opentrons_96_filtertiprack_1000ul", "1000uL")
deck.assign_child_at_slot(tip_300, 6)
deck.assign_child_at_slot(tip_1000, 9)

plate_24_deep = Cor_Axy_24_wellplate_10mL_Vb(name="plate_24_deep")
plate_96_deep = NEST_96_wellplate_2200uL_Ub(name="plate_96_deep")
plate_96_flat = Cor_96_wellplate_360ul_Fb(name="plate_96_flat")
deck.assign_child_at_slot(plate_24_deep, 1)
deck.assign_child_at_slot(plate_96_deep, 2)
deck.assign_child_at_slot(plate_96_flat, 3)


async def main():
    await lh.setup(skip_home=False)

    # ---- P1000: 24-well → 96-deepwell (with mix at source) ----
    await lh.pick_up_tips(tip_1000["A1"], use_channels=[1])
    await lh.aspirate(
        plate_24_deep["A1"],
        vols=[200],
        mix=[Mix(volume=200, repetitions=3, flow_rate=400)],
        use_channels=[1],
    )
    await lh.dispense(
        plate_96_deep["A1"],
        vols=[200],
        use_channels=[1],
    )
    await lh.return_tips()

    # ---- P300: 96-deepwell → 96-flat (with mix at source) ----
    await lh.pick_up_tips(tip_300["A1"], use_channels=[0])
    await lh.aspirate(
        plate_96_deep["A1"],
        vols=[100],
        mix=[Mix(volume=100, repetitions=3, flow_rate=400)],
        use_channels=[0],
    )
    await lh.dispense(
        plate_96_flat["A1"],
        vols=[100],
        use_channels=[0],
    )
    await lh.return_tips()

    await backend.home()


if __name__ == "__main__":
    asyncio.run(main())
