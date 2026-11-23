#крутой скрипт 228
#легендарка
print("Hello world")
#Моя любамая задача
"""
Шаблон для задачи Журнал событий в ПВЗ

В этом файле собраны все необходимые классы из урока и предыдущих задач.
Ваша задача — создать класс ActionLogger и доработать PickupPoint для логирования событий.
Классы Parcel, FrozenParcel, FragileParcel, Shelf, Fridge и другие уже реализованы.
"""

from abc import ABC, abstractmethod
from typing import Optional, List, Dict, Any
from dataclasses import dataclass, field
from enum import Enum, auto


# ============================================
# КЛАССЫ ИЗ УРОКА (БАЗОВЫЕ)
# ============================================

class IIdentifiable(ABC):
    """Интерфейс для всего, что имеет уникальный ID"""

    @property
    @abstractmethod
    def id(self) -> str:
        pass


class IStorageUnit(ABC):
    """Абстрактное место, куда можно положить посылку"""

    @abstractmethod
    def store_item(self, item: 'Parcel') -> bool:
        """Попытаться положить предмет. Вернёт True, если влезло."""
        pass

    @abstractmethod
    def retrieve_item(self, item_id: str) -> Optional['Parcel']:
        """Достать предмет, если он там есть."""
        pass

    @abstractmethod
    def get_items(self) -> List['Parcel']:
        """Получить список всех предметов."""
        pass

    @abstractmethod
    def get_capacity(self) -> float:
        """Получить вместимость."""
        pass

    @abstractmethod
    def get_current_load(self) -> float:
        """Получить текущую загрузку."""
        pass


class Human(IIdentifiable):
    """Базовый класс для всех людей"""

    def __init__(self, name: str, passport_id: str):
        self.name = name
        self._passport_id = passport_id

    @property
    def id(self) -> str:
        return self._passport_id

    def speak(self, phrase: str):
        print(f"{self.name} говорит: {phrase}")


class Employee(Human):
    """Сотрудник ПВЗ"""

    def __init__(self, name: str, passport_id: str, stress_level: int = 0):
        super().__init__(name, passport_id)
        self.stress_level = stress_level

    def work(self):
        self.stress_level += 10
        if self.stress_level > 100:
            self.speak("Я УВОЛЬНЯЮСЬ! ГДЕ МОЯ ТРУДОВАЯ?!")
        else:
            self.speak("Пакет нужен?")


class ParcelStatus(Enum):
    """Состояния посылки в системе"""
    CREATED = auto()
    IN_TRANSIT = auto()
    ARRIVED = auto()
    ISSUED = auto()
    LOST = auto()
    RETURNED = auto()


@dataclass
class Dimensions:
    """Габариты посылки"""
    length: float
    width: float
    height: float

    def volume(self) -> float:
        return self.length * self.width * self.height


@dataclass(order=True)
class Parcel:
    """Базовая посылка"""
    tracking_number: str
    weight_kg: float
    dims: Dimensions
    cost: float
    status: ParcelStatus = field(default=ParcelStatus.CREATED)
    history: List[str] = field(default_factory=list)

    def change_status(self, new_status: ParcelStatus, comment: str = ""):
        self.status = new_status
        self.history.append(f"Статус изменён на {new_status.name}. {comment}")

    def __post_init__(self):
        if self.weight_kg > 30:
            print(f"⚠️ ВНИМАНИЕ: Посылка {self.tracking_number} тяжёлая!")


class FrozenParcel(Parcel):
    """Замороженная посылка"""

    def __post_init__(self):
        super().__post_init__()
        self.max_temp_c = -5.0
        print(f"❄️ Заморозка {self.tracking_number} (требует холодильника)")

# ============================================
# КЛАСС ИЗ ЗАДАЧИ ХРУПКАЯ ПОСЫЛКА
# ============================================


class FragileParcel(Parcel):
    """Хрупкая посылка"""

    def __post_init__(self):
        super().__post_init__()
        print(f"⚠️ Хрупкая посылка {self.tracking_number}! Обращаться осторожно.")

# ============================================
# РЕАЛИЗАЦИИ ХРАНИЛИЩ (ПОЛКА И ХОЛОДИЛЬНИК)
# ============================================


class Shelf(IStorageUnit):
    """Обычная полка"""

    def __init__(self, capacity_kg: float):
        self.capacity_kg = capacity_kg
        self.current_load = 0.0
        self.items: Dict[str, Parcel] = {}
        self.is_fragile_parcel = False
        self.fragile_parcel = None

    def store_item(self, item: Parcel) -> bool:
        """Модификации из задач про замороженные и хрупкие посылки"""
        if isinstance(item, FragileParcel):
            if self.is_fragile_parcel:
                raise ValueError(f"На полке уже есть хрупкая посылка {self.fragile_parcel}")
            if self.items:
                raise ValueError(
                    f"Хрупкую посылку {item.tracking_number} нельзя класть на полку с другими товарами"
                )
            self.is_fragile_parcel = True
            self.fragile_parcel = str(item.tracking_number)
        elif self.is_fragile_parcel:
            raise ValueError(f"На полке уже есть хрупкая посылка {self.fragile_parcel}")

        if isinstance(item, FrozenParcel):
            return False

        # Проверка веса
        if self.current_load + item.weight_kg > self.capacity_kg:
            raise ValueError(
                f"Полка трещит! Нельзя положить {item.tracking_number} (перегруз)."
            )

        # Всё хорошо — кладём
        self.items[item.tracking_number] = item
        self.current_load += item.weight_kg
        print(
            f"✅ Посылка {item.tracking_number} положена на полку",
            f"(нагрузка: {self.current_load:.1f}/{self.capacity_kg} кг)."
        )
        return True

    def retrieve_item(self, item_id: str) -> Optional[Parcel]:
        item = self.items.pop(item_id, None)
        if item:
            self.current_load -= item.weight_kg
            print(f"📤 Посылка {item_id} снята с полки.")
            if item_id == self.fragile_parcel:
                self.is_fragile_parcel = False
        return item

    def get_items(self) -> List[Parcel]:
        return list(self.items.values())

    def get_capacity(self) -> float:
        return self.capacity_kg

    def get_current_load(self) -> float:
        return self.current_load


class Fridge(IStorageUnit):
    """Холодильник для замороженных товаров"""

    def __init__(self, capacity_kg: float = 50.0):
        self.capacity_kg = capacity_kg
        self.current_load = 0.0
        self.items: Dict[str, Parcel] = {}
        self.temperature_c = -18.0

    def store_item(self, item: Parcel) -> bool:
        # Холодильник принимает ТОЛЬКО замороженные товары
        if not isinstance(item, FrozenParcel):
            return False

        if self.current_load + item.weight_kg > self.capacity_kg:
            return False

        self.items[item.tracking_number] = item
        self.current_load += item.weight_kg
        return True

    def retrieve_item(self, item_id: str) -> Optional[Parcel]:
        item = self.items.pop(item_id, None)
        if item:
            self.current_load -= item.weight_kg
        return item

    def get_items(self) -> List[Parcel]:
        return list(self.items.values())

    def get_capacity(self) -> float:
        return self.capacity_kg

    def get_current_load(self) -> float:
        return self.current_load


class FloorCorner(IStorageUnit):
    """Угол для тяжёлых вещей"""

    def __init__(self, max_items: int, min_weight: float = 30.0):
        self.max_items: int = max_items
        self.items: Dict[str, Parcel] = {}
        self.min_weight: float = min_weight

    def store_item(self, item: Parcel) -> bool:
        if item.weight_kg < self.min_weight:
            return False

        if len(self.items) + 1 > self.max_items:
            return False

        self.items[item.tracking_number] = item
        return True

    def retrieve_item(self, item_id: str) -> Optional[Parcel]:
        item = self.items.pop(item_id, None)
        return item

    def get_items(self) -> List[Parcel]:
        return list(self.items.values())

    def get_capacity(self) -> float:
        return float(self.max_items)

    def get_current_load(self) -> float:
        return float(len(self.items))


class ActionLogger:
    """Журнал событий ПВЗ"""

    def __init__(self):
        self.entries: List[Dict[str, Any]] = []

    def log(self, timestamp: str, action: str, who: str, details: str = "") -> None:
        entry = {
            "timestamp": timestamp,
            "who": who,
            "action": action,
            "details": details
        }
        self.entries.append(entry)
        if details:
            print(f"[{timestamp}] {who}: {action} {details}")
        else:
            print(f"[{timestamp}] {who}: {action}")

    def get_last(self, n: int) -> List[Dict[str, Any]]:
        if n <= 0:
            return []
        return self.entries[-n:]

    def show(self) -> None:
        if not self.entries:
            print("Журнал пуст")
        else:
            print("\n=== ЖУРНАЛ СОБЫТИЙ ===")
            for entry in self.entries:
                if entry["details"]:
                    print(
                        f"[{entry['timestamp']}] {entry['who']}: "
                        f"{entry['action']} ({entry['details']})"
                    )
                else:
                    print(
                        f"[{entry['timestamp']}] {entry['who']}: {entry['action']}"
                    )

    def clear(self) -> None:
        self.entries.clear()
        print("Журнал очищен")


class PickupPoint:
    """Пункт выдачи заказов с логированием"""

    def __init__(self, address: str, manager: Employee):
        self.address = address
        self.manager = manager
        self.shelves: List[IStorageUnit] = []
        self.logger = ActionLogger()
        self.logger.log("00:00:00", "открыл ПВЗ", self.manager.name, f"по адресу {address}")

    def add_shelf(self, shelf: IStorageUnit, timestamp: str):
        """Добавить полку в ПВЗ"""
        self.shelves.append(shelf)
        self.logger.log(
            timestamp, "добавил полку", self.manager.name,
            f"вместимость {shelf.get_capacity()} кг"
        )

    def receive_parcel(self, parcel: Parcel, courier: Human, timestamp: str):
        """Процесс приёмки товара от курьера"""
        self.logger.log(timestamp, "принял посылку", courier.name, parcel.tracking_number)

        stored = False
        for shelf_idx, shelf in enumerate(self.shelves, start=1):
            try:
                if shelf.store_item(parcel):
                    stored = True
                    self.logger.log(
                        timestamp, "разместил посылку", self.manager.name,
                        f"{parcel.tracking_number} на полку {shelf_idx}"
                    )
                    break
                else:
                    self.logger.log(
                        timestamp, "не смог разместить посылку на полке",
                        self.manager.name,
                        f"{parcel.tracking_number} — полка не подходит"
                    )
            except ValueError as e:
                self.logger.log(
                    timestamp, "ошибка размещения посылки", self.manager.name,
                    f"{parcel.tracking_number}: {str(e)}"
                )

        if stored:
            parcel.change_status(ParcelStatus.ARRIVED)
        else:
            self.logger.log(
                timestamp, "НЕ удалось разместить посылку", self.manager.name,
                f"{parcel.tracking_number} — нет подходящего места"
            )
            parcel.change_status(ParcelStatus.LOST)

    def serve_client(self, client: Human, parcel_track: str, timestamp: str):
        """Выдача посылки клиенту"""
        self.logger.log(timestamp, "запрос на выдачу", client.name, parcel_track)

        found_parcel = None
        for shelf_idx, shelf in enumerate(self.shelves, start=1):
            parcel = shelf.retrieve_item(parcel_track)
            if parcel:
                found_parcel = parcel
                self.logger.log(
                    timestamp, "снял посылку", self.manager.name,
                    f"{parcel_track} с полки {shelf_idx}"
                )
            break

        if found_parcel:
            found_parcel.change_status(ParcelStatus.ISSUED)
            self.logger.log(
                timestamp, "выдал посылку", self.manager.name,
                f"{parcel_track} клиенту {client.name}"
            )
        else:
            self.logger.log(
                timestamp, "посылка не найдена", self.manager.name, parcel_track
            )
#green gaster