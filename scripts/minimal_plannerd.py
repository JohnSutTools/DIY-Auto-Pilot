#!/usr/bin/env python3
"""
Minimal plannerd for LKAS-only operation

This simplified plannerd publishes minimal longitudinalPlan and driverAssistance 
messages without actually doing longitudinal planning (speed control).
Used for LKAS-only systems where we only need lateral (steering) control.
"""
from cereal import car, log
from openpilot.common.params import Params
from openpilot.common.realtime import Priority, config_realtime_process
from openpilot.common.swaglog import cloudlog
import cereal.messaging as messaging


def main():
    config_realtime_process(5, Priority.CTRL_LOW)

    cloudlog.info("minimal_plannerd is waiting for CarParams")
    params = Params()
    CP = messaging.log_from_bytes(params.get("CarParams", block=True), car.CarParams)
    cloudlog.info(f"minimal_plannerd got CarParams: {CP.carFingerprint}")

    pm = messaging.PubMaster(['longitudinalPlan', 'driverAssistance'])
    sm = messaging.SubMaster(['carState', 'modelV2'], poll='modelV2')

    cloudlog.info("minimal_plannerd ready (LKAS-only mode)")

    while True:
        sm.update()
        
        if sm.updated['modelV2']:
            # Publish minimal longitudinalPlan
            plan_msg = messaging.new_message('longitudinalPlan')
            plan_msg.valid = True
            plan_msg.longitudinalPlan.hasLead = False
            plan_msg.longitudinalPlan.fcw = False
            # Leave velocities and accelerations as zeros (no longitudinal control)
            pm.send('longitudinalPlan', plan_msg)

            # Publish minimal driverAssistance
            assist_msg = messaging.new_message('driverAssistance')
            assist_msg.valid = sm.all_checks(['carState', 'modelV2'])
            assist_msg.driverAssistance.leftLaneDeparture = False
            assist_msg.driverAssistance.rightLaneDeparture = False
            pm.send('driverAssistance', assist_msg)


if __name__ == "__main__":
    main()
