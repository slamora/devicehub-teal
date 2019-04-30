import ipaddress
from datetime import datetime, timedelta
from decimal import Decimal
from distutils.version import StrictVersion
from typing import Dict, List, Optional, Set, Union
from uuid import UUID

from boltons import urlutils
from boltons.urlutils import URL
from sqlalchemy import Column
from sqlalchemy.orm import relationship
from sqlalchemy_utils import Currency
from teal import enums
from teal.db import Model
from teal.enums import Country

from ereuse_devicehub.resources.agent.models import Agent
from ereuse_devicehub.resources.device.models import Component, Computer, Device
from ereuse_devicehub.resources.enums import AppearanceRange, Bios, ErasureStandards, \
    FunctionalityRange, PhysicalErasureMethod, PriceSoftware, RatingSoftware, ReceiverRole, \
    Severity, SnapshotExpectedEvents, SnapshotSoftware, TestDataStorageLength, BiosAccessRange
from ereuse_devicehub.resources.models import Thing
from ereuse_devicehub.resources.user.models import User


class Event(Thing):
    id = ...  # type: Column
    name = ...  # type: Column
    type = ...  # type: Column
    description = ...  # type: Column
    snapshot_id = ...  # type: Column
    snapshot = ...  # type: relationship
    author_id = ...  # type: Column
    agent = ...  # type: relationship
    components = ...  # type: relationship
    parent_id = ...  # type: Column
    parent = ...  # type: relationship
    closed = ...  # type: Column
    start_time = ...  # type: Column
    end_time = ...  # type: Column
    agent_id = ...  # type: Column
    severity = ...  # type: Column

    def __init__(self, **kwargs) -> None:
        super().__init__(created, updated)
        self.id = ...  # type: UUID
        self.name = ...  # type: str
        self.type = ...  # type: str
        self.closed = ...  # type: bool
        self.description = ...  # type: str
        self.start_time = ...  # type: datetime
        self.end_time = ...  # type: datetime
        self.snapshot = ...  # type: Snapshot
        self.components = ...  # type: Set[Component]
        self.parent = ...  # type: Computer
        self.agent = ...  # type: Agent
        self.author = ...  # type: User
        self.severity = ...  # type: Severity

    @property
    def url(self) -> urlutils.URL:
        pass

    @property
    def elapsed(self) -> timedelta:
        pass

    @property
    def certificate(self) -> Optional[urlutils.URL]:
        return None

    @property
    def date_str(self):
        return '{:%c}'.format(self.end_time or self.created)


class EventWithOneDevice(Event):

    def __init__(self, **kwargs) -> None:
        super().__init__(**kwargs)
        self.device = ...  # type: Device


class EventWithMultipleDevices(Event):
    devices = ...  # type: relationship

    def __init__(self, **kwargs) -> None:
        super().__init__(**kwargs)
        self.devices = ...  # type: Set[Device]


class Add(EventWithOneDevice):
    pass


class Remove(EventWithOneDevice):
    pass


class Step(Model):
    type = ...  # type: Column
    num = ...  # type: Column
    start_time = ...  # type: Column
    end_time = ...  # type: Column
    erasure = ...  # type: relationship
    severity = ...  # type: Column

    def __init__(self, num=None, success=None, start_time=None, end_time=None,
                 erasure=None, severity=None) -> None:
        self.type = ...  # type: str
        self.num = ...  # type: int
        self.start_time = ...  # type: datetime
        self.end_time = ...  # type: datetime
        self.erasure = ...  # type: EraseBasic
        self.severity = ...  # type: Severity


class StepZero(Step):
    pass


class StepRandom(Step):
    pass


class EraseBasic(EventWithOneDevice):
    def __init__(self, **kwargs) -> None:
        super().__init__(**kwargs)
        self.start_time = ...  # type: datetime
        self.end_time = ...  # type: datetime
        self.steps = ...  # type: List[Step]
        self.zeros = ...  # type: bool
        self.success = ...  # type: bool

    @property
    def standards(self) -> Set[ErasureStandards]:
        pass

    @property
    def certificate(self) -> urlutils.URL:
        pass


class EraseSectors(EraseBasic):
    def __init__(self, **kwargs) -> None:
        super().__init__(**kwargs)


class ErasePhysical(EraseBasic):
    method = ...  # type: Column

    def __init__(self, **kwargs) -> None:
        super().__init__(**kwargs)
        self.method = ...  # type: PhysicalErasureMethod


class Snapshot(EventWithOneDevice):
    def __init__(self, **kwargs) -> None:
        super().__init__(**kwargs)
        self.uuid = ...  # type: UUID
        self.version = ...  # type: StrictVersion
        self.software = ...  # type: SnapshotSoftware
        self.elapsed = ...  # type: timedelta
        self.device = ...  # type: Computer
        self.events = ...  # type: Set[Event]
        self.expected_events = ...  # type: List[SnapshotExpectedEvents]


class Install(EventWithOneDevice):
    name = ...  # type: Column
    elapsed = ...  # type: Column
    address = ...  # type: Column

    def __init__(self, **kwargs) -> None:
        super().__init__(**kwargs)
        self.name = ...  # type: str
        self.elapsed = ...  # type: timedelta
        self.address = ...  # type: Optional[int]


class SnapshotRequest(Mod    assert rate_computer.rating == 4.61
el):
    def __init__(self, **kwargs) -> None:
        self.id = ...  # type: UUID
        self.request = ...  # type: dict
        self.snapshot = ...  # type: Snapshot


class Benchmark(EventWithOneDevice):
    pass


class BenchmarkDataStorage(Benchmark):
    read_speed = ...  # type: Column
    write_speed = ...  # type: Column

    def __init__(self, **kwargs) -> None:
        super().__init__(**kwargs)
        self.read_speed = ...  # type: float
        self.write_speed = ...  # type: float


class BenchmarkWithRate(Benchmark):
    rate = ...  # type: Column

    def __init__(self, **kwargs) -> None:
        super().__init__(**kwargs)
        self.rate = ...  # type: int


class BenchmarkProcessor(BenchmarkWithRate):
    pass


class BenchmarkProcessorSysbench(BenchmarkProcessor):
    pass


class BenchmarkRamSysbench(BenchmarkWithRate):
    pass


class BenchmarkGraphicCard(BenchmarkWithRate):
    pass


class Test(EventWithOneDevice):
    elapsed = ...  # type: Column
    def __init__(self, **kwargs) -> None:
        super().__init__(**kwargs)
        self.elapsed = ...  # type: Optional[timedelta]
        self.success = ...  # type: bool


class TestDataStorage(Test):
    def __init__(self, **kwargs) -> None:
        super().__init__(**kwargs)
        self.id = ...  # type: UUID
        self.length = ...  # type: TestDataStorageLength
        self.status = ...  # type: str
        self.lifetime = ...  # type: timedelta
        self.first_error = ...  # type: int
        self.passed_lifetime = ...  # type: timedelta
        self.assessment = ...  # type: int
        self.reallocated_sector_count = ...  # type: int
        self.power_cycle_count = ...  # type: int
        self.reported_uncorrectable_errors = ...  # type: int
        self.command_timeout = ...  # type: int
        self.current_pending_sector_count = ...  # type: int
        self.offline_uncorrectable = ...  # type: int
        self.remaining_lifetime_percentage = ...  # type: int


class StressTest(Test):
    pass


class TestAudio(Test):
    """
    Test to check all this aspects related with audio functions, Manual Tests??
    """
    loudspeaker = ...  # type: Column
    microphone = ...  # type: Column


class TestConnectivity(Test):
    cellular_network = ...  # type: Column
    wifi = ...  # type: Column
    bluetooth = ...  # type: Column
    usb_port = ...  # type: Column
    locked = ...  # type: Column


class TestBattery(Test):
    battery_stat = ...  # type: Column
    battery_health = ...  # type: Column


class TestCamera(Test):
    camera = ...  # type: Column


class TestKeyboard(Test):
    keyboard = ...  # type: Column


class TestTrackpad(Test):
    trackpad = ...  # type: Column


class TestBios(Test):
    bios_power_on = ...  # type: Column
    access_range = ...  # type: BiosAccessRange


class TestVisual(ManualRate):
    appearance_range = ...  # type: AppearanceRange
    functionality_range = ...  # type: FunctionalityRange
    labelling = ...  # type: Column


class Rate(EventWithOneDevice):
    rating = ...  # type: Column
    appearance = ...  # type: Column
    functionality = ...  # type: Column
    version = ...  # type: Column

    def __init__(self, **kwargs) -> None:
        super().__init__(**kwargs)
        self.rating = ...  # type: float
        self.software = ...  # type: RatingSoftware
        self.version = ...  # type: StrictVersion
        self.appearance = ...  # type: float
        self.functionality = ...  # type: float
        self.rating_range = ...  # type: str


class RateComputer(Rate):
    id = ...
    processor = ...
    ram = ...
    data_storage = ...

    @classmethod
    def compute(cls, device):
        pass


class Price(EventWithOneDevice):
    SCALE = ...
    ROUND = ...
    currency = ...  # type: Column
    price = ...  # type: Column
    software = ...  # type: Column
    version = ...  # type: Column
    rating_id = ...  # type: Column
    rating = ...  # type: relationship

    def __init__(self, **kwargs) -> None:
        super().__init__(**kwargs)
        self.price = ...  # type: Decimal
        self.currency = ...  # type: Currency
        self.software = ...  # type: PriceSoftware
        self.version = ...  # type: StrictVersion
        self.rating = ...  # type: Rate

    @classmethod
    def to_price(cls, value: Union[Decimal, float], rounding=ROUND) -> Decimal:
        pass


class EreusePrice(Price):
    MULTIPLIER = ...  # type: Dict

    class Type:
        def __init__(self, percentage, price) -> None:
            super().__init__()
            self.amount = ...  # type: float
            self.percentage = ...  # type: float

    class Service:
        def __init__(self) -> None:
            super().__init__()
            self.standard = ...  # type: EreusePrice.Type
            self.warranty2 = ...  # type: EreusePrice.Type

    def __init__(self, rating: Rate, **kwargs) -> None:
        super().__init__(**kwargs)
        self.retailer = ...  # type: EreusePrice.Service
        self.platform = ...  # type: EreusePrice.Service
        self.refurbisher = ...  # type: EreusePrice.Service
        self.warranty2 = ...  # type: float


class ToRepair(EventWithMultipleDevices):
    pass


class Repair(EventWithMultipleDevices):
    pass


class ReadyToUse(EventWithMultipleDevices):
    pass


class ToPrepare(EventWithMultipleDevices):
    pass


class Prepare(EventWithMultipleDevices):
    pass


class Live(EventWithOneDevice):
    ip = ...  # type: Column
    subdivision_confidence = ...  # type: Column
    subdivision = ...  # type: Column
    city = ...  # type: Column
    city_confidence = ...  # type: Column
    isp = ...  # type: Column
    organization = ...  # type: Column
    organization_type = ...  # type: Column

    def __init__(self, **kwargs) -> None:
        super().__init__(**kwargs)
        self.ip = ...  # type: Union[ipaddress.IPv4Address, ipaddress.IPv6Address]
        self.subdivision_confidence = ...  # type: int
        self.subdivision = ...  # type: enums.Subdivision
        self.city = ...  # type: str
        self.city_confidence = ...  # type: int
        self.isp = ...  # type: str
        self.organization = ...  # type: str
        self.organization_type = ...  # type: str
        self.country = ...  # type: Country


class Organize(EventWithMultipleDevices):
    pass


class Reserve(Organize):
    pass


class Trade(EventWithMultipleDevices):
    shipping_date = ...  # type: Column
    invoice_number = ...  # type: Column
    price = ...  # type: relationship
    to = ...  # type: relationship
    confirms = ...  # type: relationship

    def __init__(self, **kwargs) -> None:
        super().__init__(**kwargs)
        self.shipping_date = ...  # type: datetime
        self.invoice_number = ...  # type: str
        self.price = ...  # type: Price
        self.to = ...  # type: Agent
        self.confirms = ...  # type: Organize


class Sell(Trade):
    pass


class Donate(Trade):
    pass


class Rent(Trade):
    pass


class CancelTrade(Trade):
    pass


class ToDisposeProduct(Trade):
    pass


class DisposeProduct(Trade):
    pass


class Receive(EventWithMultipleDevices):
    role = ...  # type:Column

    def __init__(self, **kwargs) -> None:
        super().__init__(**kwargs)
        self.role = ...  # type: ReceiverRole


class Migrate(EventWithMultipleDevices):
    other = ...  # type: Column

    def __init__(self, **kwargs) -> None:
        super().__init__(**kwargs)
        self.other = ...  # type: URL


class MigrateTo(Migrate):
    pass


class MigrateFrom(Migrate):
    pass
