from marshmallow import post_load, pre_load
from marshmallow.fields import Boolean, DateTime, Float, Integer, List, Str, String
from marshmallow.validate import Length, OneOf, Range
from sqlalchemy.util import OrderedSet
from stdnum import imei, meid
from teal.enums import Layouts
from teal.marshmallow import EnumField, SanitizedStr, URL, ValidationError
from teal.resource import Schema

from ereuse_devicehub.marshmallow import NestedOn
from ereuse_devicehub.resources import enums
from ereuse_devicehub.resources.device import models as m, states
from ereuse_devicehub.resources.models import STR_BIG_SIZE, STR_SIZE
from ereuse_devicehub.resources.schemas import Thing, UnitCodes


class Device(Thing):
    __doc__ = m.Device.__doc__
    id = Integer(description=m.Device.id.comment, dump_only=True)
    hid = SanitizedStr(lower=True, dump_only=True, description=m.Device.hid.comment)
    tags = NestedOn('Tag',
                    many=True,
                    collection_class=OrderedSet,
                    description='A set of tags that identify the device.')
    model = SanitizedStr(lower=True,
                         validate=Length(max=STR_BIG_SIZE),
                         description=m.Device.model.comment)
    manufacturer = SanitizedStr(lower=True,
                                validate=Length(max=STR_SIZE),
                                description=m.Device.manufacturer.comment)
    serial_number = SanitizedStr(lower=True,
                                 validate=Length(max=STR_BIG_SIZE),
                                 data_key='serialNumber')
    brand = SanitizedStr(validate=Length(max=STR_BIG_SIZE), description=m.Device.brand.comment)
    generation = Integer(validate=Range(1, 100), description=m.Device.generation.comment)
    weight = Float(validate=Range(0.1, 5), unit=UnitCodes.kgm, description=m.Device.weight.comment)
    width = Float(validate=Range(0.1, 5), unit=UnitCodes.m, description=m.Device.width.comment)
    height = Float(validate=Range(0.1, 5), unit=UnitCodes.m, description=m.Device.height.comment)
    depth = Float(validate=Range(0.1, 5), unit=UnitCodes.m, description=m.Device.depth.comment)
    events = NestedOn('Event', many=True, dump_only=True, description=m.Device.events.__doc__)
    events_one = NestedOn('Event', many=True, load_only=True, collection_class=OrderedSet)
    problems = NestedOn('Event', many=True, dump_only=True, description=m.Device.problems.__doc__)
    url = URL(dump_only=True, description=m.Device.url.__doc__)
    lots = NestedOn('Lot',
                    many=True,
                    dump_only=True,
                    description='The lots where this device is directly under.')
    rate = NestedOn('AggregateRate', dump_only=True, description=m.Device.rate.__doc__)
    price = NestedOn('Price', dump_only=True, description=m.Device.price.__doc__)
    trading = EnumField(states.Trading, dump_only=True, description=m.Device.trading.__doc__)
    physical = EnumField(states.Physical, dump_only=True, description=m.Device.physical.__doc__)
    physical_possessor = NestedOn('Agent', dump_only=True, data_key='physicalPossessor')
    production_date = DateTime('iso',
                               description=m.Device.updated.comment,
                               data_key='productionDate')
    working = NestedOn('Event',
                       many=True,
                       dump_only=True,
                       description=m.Device.working.__doc__)

    @pre_load
    def from_events_to_events_one(self, data: dict):
        """
        Not an elegant way of allowing submitting events to a device
        (in the context of Snapshots) without creating an ``events``
        field at the model (which is not possible).
        :param data:
        :return:
        """
        # Note that it is secure to allow uploading events_one
        # as the only time an user can send a device object is
        # in snapshots.
        data['events_one'] = data.pop('events', [])
        return data

    @post_load
    def validate_snapshot_events(self, data):
        """Validates that only snapshot-related events can be uploaded."""
        from ereuse_devicehub.resources.event.models import EraseBasic, Test, Rate, Install, \
            Benchmark
        for event in data['events_one']:
            if not isinstance(event, (Install, EraseBasic, Rate, Test, Benchmark)):
                raise ValidationError('You cannot upload {}'.format(event), field_names=['events'])


class Computer(Device):
    __doc__ = m.Computer.__doc__
    components = NestedOn('Component',
                          many=True,
                          dump_only=True,
                          collection_class=OrderedSet,
                          description='The components that are inside this computer.')
    chassis = EnumField(enums.ComputerChassis,
                        required=True,
                        description=m.Computer.chassis.comment)
    ram_size = Integer(dump_only=True,
                       data_key='ramSize',
                       description=m.Computer.ram_size.__doc__)
    data_storage_size = Integer(dump_only=True,
                                data_key='dataStorageSize',
                                description=m.Computer.data_storage_size.__doc__)
    processor_model = Str(dump_only=True,
                          data_key='processorModel',
                          description=m.Computer.processor_model.__doc__)
    graphic_card_model = Str(dump_only=True,
                             data_key='graphicCardModel',
                             description=m.Computer.graphic_card_model.__doc__)
    network_speeds = List(Integer(dump_only=True),
                          dump_only=True,
                          data_key='networkSpeeds',
                          description=m.Computer.network_speeds.__doc__)
    privacy = NestedOn('Event',
                       many=True,
                       dump_only=True,
                       collection_class=set,
                       description=m.Computer.privacy.__doc__)


class Desktop(Computer):
    __doc__ = m.Desktop.__doc__


class Laptop(Computer):
    __doc__ = m.Laptop.__doc__
    layout = EnumField(Layouts, description=m.Laptop.layout.comment)


class Server(Computer):
    __doc__ = m.Server.__doc__


class DisplayMixin:
    __doc__ = m.DisplayMixin.__doc__
    size = Float(description=m.DisplayMixin.size.comment, validate=Range(2, 150), required=True)
    technology = EnumField(enums.DisplayTech,
                           description=m.DisplayMixin.technology.comment)
    resolution_width = Integer(data_key='resolutionWidth',
                               validate=Range(10, 20000),
                               description=m.DisplayMixin.resolution_width.comment,
                               required=True)
    resolution_height = Integer(data_key='resolutionHeight',
                                validate=Range(10, 20000),
                                description=m.DisplayMixin.resolution_height.comment,
                                required=True)
    refresh_rate = Integer(data_key='refreshRate', validate=Range(10, 1000))
    contrast_ratio = Integer(data_key='contrastRatio', validate=Range(100, 100000))
    touchable = Boolean(description=m.DisplayMixin.touchable.comment)
    aspect_ratio = String(dump_only=True, description=m.DisplayMixin.aspect_ratio.__doc__)
    widescreen = Boolean(dump_only=True, description=m.DisplayMixin.widescreen.__doc__)


class NetworkMixin:
    __doc__ = m.NetworkMixin.__doc__

    speed = Integer(validate=Range(min=10, max=10000),
                    unit=UnitCodes.mbps,
                    description=m.NetworkAdapter.speed.comment)
    wireless = Boolean(required=True)


class Monitor(DisplayMixin, Device):
    __doc__ = m.Monitor.__doc__


class ComputerMonitor(Monitor):
    __doc__ = m.ComputerMonitor.__doc__


class TelevisionSet(Monitor):
    __doc__ = m.TelevisionSet.__doc__


class Mobile(Device):
    __doc__ = m.Mobile.__doc__

    imei = Integer(description=m.Mobile.imei.comment)
    meid = Str(description=m.Mobile.meid.comment)
    ram_size = Integer(validate=Range(min=128, max=36000),
                       data_key='ramSize',
                       unit=UnitCodes.mbyte,
                       description=m.Mobile.ram_size.comment)
    data_storage_size = Integer(validate=Range(0, 10 ** 8),
                                data_key='dataStorageSize',
                                description=m.Mobile.data_storage_size)


    @pre_load
    def convert_check_imei(self, data):
        if data.get('imei', None):
            data['imei'] = int(imei.validate(data['imei']))
        return data

    @pre_load
    def convert_check_meid(self, data: dict):
        if data.get('meid', None):
            data['meid'] = meid.compact(data['meid'])
        return data


class Smartphone(Mobile):
    __doc__ = m.Smartphone.__doc__


class Tablet(Mobile):
    __doc__ = m.Tablet.__doc__


class Cellphone(Mobile):
    __doc__ = m.Cellphone.__doc__


class Component(Device):
    __doc__ = m.Component.__doc__

    parent = NestedOn(Device, dump_only=True)


class GraphicCard(Component):
    __doc__ = m.GraphicCard.__doc__

    memory = Integer(validate=Range(0, 10000),
                     unit=UnitCodes.mbyte,
                     description=m.GraphicCard.memory.comment)


class DataStorage(Component):
    __doc__ = m.DataStorage.__doc__

    size = Integer(validate=Range(0, 10 ** 8),
                   unit=UnitCodes.mbyte,
                   description=m.DataStorage.size.comment)
    interface = EnumField(enums.DataStorageInterface)
    privacy = NestedOn('Event', dump_only=True)


class HardDrive(DataStorage):
    __doc__ = m.HardDrive.__doc__


class SolidStateDrive(DataStorage):
    __doc__ = m.SolidStateDrive.__doc__


class Motherboard(Component):
    __doc__ = m.Motherboard.__doc__

    slots = Integer(validate=Range(0, 20),
                    description=m.Motherboard.slots.comment)
    usb = Integer(validate=Range(0, 20), description=m.Motherboard.usb.comment)
    firewire = Integer(validate=Range(0, 20), description=m.Motherboard.firewire.comment)
    serial = Integer(validate=Range(0, 20), description=m.Motherboard.serial.comment)
    pcmcia = Integer(validate=Range(0, 20), description=m.Motherboard.pcmcia.comment)


class NetworkAdapter(NetworkMixin, Component):
    __doc__ = m.NetworkAdapter.__doc__


class Processor(Component):
    __doc__ = m.Processor.__doc__

    speed = Float(validate=Range(min=0.1, max=15),
                  unit=UnitCodes.ghz,
                  description=m.Processor.speed.comment)
    cores = Integer(validate=Range(min=1, max=10), description=m.Processor.cores.comment)
    threads = Integer(validate=Range(min=1, max=20), description=m.Processor.threads.comment)
    address = Integer(validate=OneOf({8, 16, 32, 64, 128, 256}),
                      description=m.Processor.address.comment)
    abi = SanitizedStr(lower=True, description=m.Processor.abi.comment)


class RamModule(Component):
    __doc__ = m.RamModule.__doc__

    size = Integer(validate=Range(min=128, max=17000),
                   unit=UnitCodes.mbyte,
                   description=m.RamModule.size.comment)
    speed = Integer(validate=Range(min=100, max=10000), unit=UnitCodes.mhz)
    interface = EnumField(enums.RamInterface)
    format = EnumField(enums.RamFormat)


class SoundCard(Component):
    __doc__ = m.SoundCard.__doc__


class Display(DisplayMixin, Component):
    __doc__ = m.Display.__doc__


class Battery(Component):
    __doc__ = m.Battery

    wireless = Boolean(description=m.Battery.wireless.comment)
    technology = EnumField(enums.BatteryTechnology, description=m.Battery.technology.comment)
    size = Integer(required=True, description=m.Battery.size.comment)


class Manufacturer(Schema):
    __doc__ = m.Manufacturer.__doc__

    name = String(dump_only=True)
    url = URL(dump_only=True)
    logo = URL(dump_only=True)


class ComputerAccessory(Device):
    __doc__ = m.ComputerAccessory.__doc__


class Mouse(ComputerAccessory):
    __doc__ = m.Mouse.__doc__


class MemoryCardReader(ComputerAccessory):
    __doc__ = m.MemoryCardReader.__doc__


class SAI(ComputerAccessory):
    __doc__ = m.SAI.__doc__


class Keyboard(ComputerAccessory):
    __doc__ = m.Keyboard.__doc__

    layout = EnumField(Layouts)


class Networking(NetworkMixin, Device):
    __doc__ = m.Networking.__doc__


class Router(Networking):
    __doc__ = m.Router.__doc__


class Switch(Networking):
    __doc__ = m.Switch.__doc__


class Hub(Networking):
    __doc__ = m.Hub.__doc__


class WirelessAccessPoint(Networking):
    __doc__ = m.WirelessAccessPoint.__doc__


class Printer(Device):
    __doc__ = m.Printer.__doc__

    wireless = Boolean(required=True, missing=False, description=m.Printer.wireless.comment)
    scanning = Boolean(required=True, missing=False, description=m.Printer.scanning.comment)
    technology = EnumField(enums.PrinterTechnology,
                           required=True,
                           description=m.Printer.technology.comment)
    monochrome = Boolean(required=True, missing=True, description=m.Printer.monochrome.comment)


class LabelPrinter(Printer):
    __doc__ = m.LabelPrinter.__doc__


class Sound(Device):
    __doc__ = m.Sound.__doc__


class Microphone(Sound):
    __doc__ = m.Microphone.__doc__


class Video(Device):
    __doc__ = m.Video.__doc__


class VideoScaler(Video):
    __doc__ = m.VideoScaler.__doc__


class Videoconference(Video):
    __doc__ = m.Videoconference.__doc__


class Cooking(Device):
    __doc__ = m.Cooking.__doc__


class Mixer(Cooking):
    __doc__ = m.Mixer.__doc__
