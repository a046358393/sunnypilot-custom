"""
Copyright (c) 2021-, Haibin Wen, sunnypilot, and a number of other contributors.

This file is part of sunnypilot and is licensed under the MIT License.
See the LICENSE.md file in the root directory for more details.
"""
from openpilot.selfdrive.ui.sunnypilot.layouts.settings.vehicle.brands.base import BrandSettings
from openpilot.selfdrive.ui.ui_state import ui_state
from openpilot.system.ui.lib.application import gui_app
from openpilot.system.ui.lib.multilang import tr, tr_noop
from openpilot.system.ui.widgets import DialogResult
from openpilot.system.ui.widgets.confirm_dialog import ConfirmDialog
from openpilot.system.ui.sunnypilot.widgets.list_view import toggle_item_sp
from opendbc.car.toyota.values import CAR, ToyotaFlags, TSS2_CAR, RADAR_ACC_CAR, SECOC_CAR


ONROAD_ONLY_DESCRIPTION = tr_noop("Start the vehicle to check vehicle compatibility.")
SNG_HACK_UNAVAILABLE = tr_noop("sunnypilot Longitudinal Control must be available and enabled for your vehicle to use this feature.")
PLATFORM_UNAVAILABLE = tr_noop("This feature is currently not available on this platform.")

DESCRIPTIONS = {
  'enforce_stock_longitudinal': tr_noop(
    'sunnypilot will not take over control of gas and brakes. Factory Toyota longitudinal control will be used.'
  ),
  'stop_and_go_hack': tr_noop(
    'sunnypilot will allow some Toyota/Lexus cars to auto resume during stop and go traffic. ' +
    'This feature is only applicable to certain models that are able to use longitudinal control. This is an alpha feature. Use at your own risk.'
  ),
  'tss2_smooth': tr_noop(
    'Enable smoother longitudinal control for TSS2 vehicles. ' +
    'Uses a custom speed-dependent integral gain curve for smoother traffic driving.'
  ),
  'auto_brake_hold': tr_noop(
    'Alpha feature for supported TSS2 vehicles. Holds the vehicle at a stop with cruise off. ' +
    'This modifies the vehicle brake/AEB message path. Enable only after controlled validation.'
  ),
  'brake_onset': tr_noop(
    'Softens the start of longitudinal braking and applies hybrid brake handover and overshoot corrections. ' +
    'This changes vehicle deceleration behaviour and requires careful controlled validation.'
  ),
  'drive_mode': tr_noop(
    'Links Toyota ECO/NORMAL/SPORT drive mode signals to the sunnypilot acceleration profile. ' +
    'Enables the acceleration profile controller automatically.'
  ),
}


class ToyotaSettings(BrandSettings):
  def __init__(self):
    super().__init__()

    self.enforce_stock_longitudinal = toggle_item_sp(
      lambda: tr("Enforce Factory Longitudinal Control"),
      description=lambda: tr(DESCRIPTIONS["enforce_stock_longitudinal"]),
      initial_state=ui_state.params.get_bool("ToyotaEnforceStockLongitudinal"),
      callback=self._on_enable_enforce_stock_longitudinal,
      enabled=lambda: not ui_state.engaged,
    )

    self.stop_and_go_hack = toggle_item_sp(
      lambda: tr("Stop and Go Hack (Alpha)"),
      description=lambda: tr(DESCRIPTIONS["stop_and_go_hack"]),
      initial_state=ui_state.params.get_bool("ToyotaStopAndGoHack"),
      callback=self._on_enable_stop_and_go_hack,
      enabled=lambda: not ui_state.engaged,
    )

    self.tss2_smooth = toggle_item_sp(
      lambda: tr("TSS2 Smooth Longitudinal (Alpha)"),
      description=lambda: tr(DESCRIPTIONS["tss2_smooth"]),
      initial_state=ui_state.params.get_bool("ToyotaTSS2Smooth"),
      callback=self._on_enable_tss2_smooth,
      enabled=lambda: not ui_state.engaged,
    )

    self.auto_brake_hold = toggle_item_sp(
      lambda: tr("Toyota Auto Brake Hold (Alpha)"),
      description=lambda: tr(DESCRIPTIONS["auto_brake_hold"]),
      initial_state=ui_state.params.get_bool("ToyotaAutoHold"),
      callback=self._on_enable_auto_brake_hold,
      enabled=lambda: not ui_state.engaged,
    )

    self.brake_onset = toggle_item_sp(
      lambda: tr("Toyota Soft Brake Onset (Alpha)"),
      description=lambda: tr(DESCRIPTIONS["brake_onset"]),
      initial_state=ui_state.params.get_bool("ToyotaBrakeOnset"),
      callback=self._on_enable_brake_onset,
      enabled=lambda: not ui_state.engaged,
    )

    self.drive_mode = toggle_item_sp(
      lambda: tr("Link Toyota Drive Mode to Acceleration Profile"),
      description=lambda: tr(DESCRIPTIONS["drive_mode"]),
      initial_state=ui_state.params.get_bool("ToyotaDriveMode"),
      callback=self._on_enable_drive_mode,
      enabled=lambda: not ui_state.engaged,
    )

    self.items = [
      self.enforce_stock_longitudinal,
      self.stop_and_go_hack,
      self.tss2_smooth,
      self.auto_brake_hold,
      self.brake_onset,
      self.drive_mode,
    ]

  def _on_enable_enforce_stock_longitudinal(self, state: bool):
    if state:
      def confirm_callback(result: int):
        if result == DialogResult.CONFIRM:
          ui_state.params.put_bool("ToyotaEnforceStockLongitudinal", True)
          if ui_state.params.get_bool("AlphaLongitudinalEnabled"):
            ui_state.params.put_bool("AlphaLongitudinalEnabled", False)
          ui_state.params.put_bool("ToyotaStopAndGoHack", False)
          self.stop_and_go_hack.action_item.set_state(False)
          ui_state.params.put_bool("ToyotaTSS2Smooth", False)
          self.tss2_smooth.action_item.set_state(False)
          ui_state.params.put_bool("ToyotaBrakeOnset", False)
          self.brake_onset.action_item.set_state(False)
          ui_state.params.put_bool("ToyotaDriveMode", False)
          self.drive_mode.action_item.set_state(False)
          ui_state.params.put_bool("OnroadCycleRequested", True)
        else:
          self.enforce_stock_longitudinal.action_item.set_state(False)

      content = (f"<h1>{self.enforce_stock_longitudinal.title}</h1><br>" +
                 f"<p>{self.enforce_stock_longitudinal.description}</p>")

      dlg = ConfirmDialog(content, tr("Enable"), rich=True, callback=confirm_callback)
      gui_app.push_widget(dlg)

    else:
      ui_state.params.put_bool("ToyotaEnforceStockLongitudinal", False)
      ui_state.params.put_bool("OnroadCycleRequested", True)

  def _on_enable_tss2_smooth(self, state: bool):
    if state:
      def confirm_callback(result: int):
        if result == DialogResult.CONFIRM:
          ui_state.params.put_bool("ToyotaTSS2Smooth", True)
          ui_state.params.put_bool("OnroadCycleRequested", True)
        else:
          self.tss2_smooth.action_item.set_state(False)

      content = (f"<h1>{self.tss2_smooth.title}</h1><br>" +
                 f"<p>{self.tss2_smooth.description}</p>")

      dlg = ConfirmDialog(content, tr("Enable"), rich=True, callback=confirm_callback)
      gui_app.push_widget(dlg)

    else:
      ui_state.params.put_bool("ToyotaTSS2Smooth", False)
      ui_state.params.put_bool("OnroadCycleRequested", True)

  def _on_enable_stop_and_go_hack(self, state: bool):
    if state:
      def confirm_callback(result: int):
        if result == DialogResult.CONFIRM:
          ui_state.params.put_bool("ToyotaStopAndGoHack", True)
          ui_state.params.put_bool("OnroadCycleRequested", True)
        else:
          self.stop_and_go_hack.action_item.set_state(False)

      content = (f"<h1>{self.stop_and_go_hack.title}</h1><br>" +
                 f"<p>{self.stop_and_go_hack.description}</p>")

      dlg = ConfirmDialog(content, tr("Enable"), rich=True, callback=confirm_callback)
      gui_app.push_widget(dlg)

    else:
      ui_state.params.put_bool("ToyotaStopAndGoHack", False)
      ui_state.params.put_bool("OnroadCycleRequested", True)

  def _on_enable_auto_brake_hold(self, state: bool):
    if state:
      def confirm_callback(result: int):
        if result == DialogResult.CONFIRM:
          ui_state.params.put_bool("ToyotaAutoHold", True)
          ui_state.params.put_bool("OnroadCycleRequested", True)
        else:
          self.auto_brake_hold.action_item.set_state(False)

      content = (f"<h1>{self.auto_brake_hold.title}</h1><br>" +
                 f"<p>{self.auto_brake_hold.description}</p>")
      dlg = ConfirmDialog(content, tr("Enable"), rich=True, callback=confirm_callback)
      gui_app.push_widget(dlg)
    else:
      ui_state.params.put_bool("ToyotaAutoHold", False)
      ui_state.params.put_bool("OnroadCycleRequested", True)

  def _on_enable_brake_onset(self, state: bool):
    if state:
      def confirm_callback(result: int):
        if result == DialogResult.CONFIRM:
          ui_state.params.put_bool("ToyotaBrakeOnset", True)
          ui_state.params.put_bool("OnroadCycleRequested", True)
        else:
          self.brake_onset.action_item.set_state(False)

      content = (f"<h1>{self.brake_onset.title}</h1><br>" +
                 f"<p>{self.brake_onset.description}</p>")
      dlg = ConfirmDialog(content, tr("Enable"), rich=True, callback=confirm_callback)
      gui_app.push_widget(dlg)
    else:
      ui_state.params.put_bool("ToyotaBrakeOnset", False)
      ui_state.params.put_bool("OnroadCycleRequested", True)

  def _on_enable_drive_mode(self, state: bool):
    if state:
      def confirm_callback(result: int):
        if result == DialogResult.CONFIRM:
          ui_state.params.put_bool("ToyotaDriveMode", True)
          ui_state.params.put_bool("AccelPersonalityEnabled", True)
          ui_state.params.put_bool("OnroadCycleRequested", True)
        else:
          self.drive_mode.action_item.set_state(False)

      content = (f"<h1>{self.drive_mode.title}</h1><br>" +
                 f"<p>{self.drive_mode.description}</p>")
      dlg = ConfirmDialog(content, tr("Enable"), rich=True, callback=confirm_callback)
      gui_app.push_widget(dlg)
    else:
      ui_state.params.put_bool("ToyotaDriveMode", False)
      ui_state.params.put_bool("OnroadCycleRequested", True)

  def update_settings(self):
    if ui_state.CP is not None:
      longitudinal = ui_state.CP.openpilotLongitudinalControl
      enforce_stock = self.enforce_stock_longitudinal.action_item.get_state()

      if longitudinal and not enforce_stock:
        self.stop_and_go_hack.action_item.set_enabled(not ui_state.engaged)
        new_desc = tr(DESCRIPTIONS["stop_and_go_hack"])
        show_desc = False
      else:
        self.stop_and_go_hack.action_item.set_enabled(False)
        self.stop_and_go_hack.action_item.set_state(False)
        new_desc = "<b>" + tr(SNG_HACK_UNAVAILABLE) + "</b>\n\n" + tr(DESCRIPTIONS["stop_and_go_hack"])
        show_desc = True

      if self.stop_and_go_hack.description != new_desc:
        self.stop_and_go_hack.set_description(new_desc)
        if show_desc:
          self.stop_and_go_hack.show_description(True)

      tss2 = bool(ui_state.CP.flags & ToyotaFlags.TSS2)
      if longitudinal and not enforce_stock and tss2:
        self.tss2_smooth.action_item.set_enabled(not ui_state.engaged)
        new_desc = tr(DESCRIPTIONS["tss2_smooth"])
        show_desc = False
      else:
        self.tss2_smooth.action_item.set_enabled(False)
        self.tss2_smooth.action_item.set_state(False)
        unavailable = SNG_HACK_UNAVAILABLE if tss2 else PLATFORM_UNAVAILABLE
        new_desc = "<b>" + tr(unavailable) + "</b>\n\n" + tr(DESCRIPTIONS["tss2_smooth"])
        show_desc = True

      if self.tss2_smooth.description != new_desc:
        self.tss2_smooth.set_description(new_desc)
        if show_desc:
          self.tss2_smooth.show_description(True)

      auto_hold_supported = ui_state.CP.carFingerprint in (TSS2_CAR - RADAR_ACC_CAR - SECOC_CAR)
      self.auto_brake_hold.action_item.set_enabled(auto_hold_supported and not ui_state.engaged)
      brake_onset_supported = (longitudinal and not enforce_stock and
                               ui_state.CP.carFingerprint == CAR.TOYOTA_COROLLA_TSS2 and
                               bool(ui_state.CP.flags & ToyotaFlags.HYBRID))
      self.brake_onset.action_item.set_enabled(brake_onset_supported and not ui_state.engaged)
      self.drive_mode.action_item.set_enabled(tss2 and not ui_state.engaged)
    else:
      self.stop_and_go_hack.action_item.set_enabled(False)
      new_desc = "<b>" + tr(ONROAD_ONLY_DESCRIPTION) + "</b>\n\n" + tr(DESCRIPTIONS["stop_and_go_hack"])
      if self.stop_and_go_hack.description != new_desc:
        self.stop_and_go_hack.set_description(new_desc)
        self.stop_and_go_hack.show_description(True)

      self.tss2_smooth.action_item.set_enabled(False)
      self.auto_brake_hold.action_item.set_enabled(False)
      self.brake_onset.action_item.set_enabled(False)
      self.drive_mode.action_item.set_enabled(False)
      new_desc = "<b>" + tr(ONROAD_ONLY_DESCRIPTION) + "</b>\n\n" + tr(DESCRIPTIONS["tss2_smooth"])
      if self.tss2_smooth.description != new_desc:
        self.tss2_smooth.set_description(new_desc)
        self.tss2_smooth.show_description(True)
