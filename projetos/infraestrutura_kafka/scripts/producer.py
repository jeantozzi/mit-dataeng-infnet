import queue
import random
import threading
import time
from dataclasses import dataclass, asdict
from typing import Optional
import json
from confluent_kafka import Producer, KafkaException, KafkaError

BROKERS = "kafka-broker-1:9092,kafka-broker-2:9092,kafka-broker-3:9092"
TOPIC = "transaction"

@dataclass
class Transaction:
    timestamp: int
    transaction_id: int
    user_id: int
    card_id: int
    site_id: int
    value: float
    location_id: int
    country: str

class TransactionGenerator:
    _transactions_queue: queue.Queue
    _trans_per_sec: int
    _fraudulent_transactions_freq: int
    _COUNTRIES: list[str] = ["USA", "Canada", "Germany", "France", "UK", "Brazil",
                             "Australia"]

    def __init__(self, trans_per_sec: int = 10, fraudulent_transactions_freq: int = 10,
                 max_queue_size: int = 1000):
        self._transactions_queue = queue.Queue(maxsize=max_queue_size)
        self._trans_per_sec = trans_per_sec
        self._fraudulent_transactions_freq = fraudulent_transactions_freq

    def generate_valid_transaction(self,
                                   timestamp: Optional[int] = None,
                                   transaction_id: Optional[int] = None,
                                   user_id: Optional[int] = None,
                                   card_id: Optional[int] = None,
                                   site_id: Optional[int] = None,
                                   value: Optional[float] = None,
                                   location: Optional[int] = None,
                                   country: Optional[str] = None) -> Transaction:
        user_id = user_id or random.randint(11000, 19999)
        tx = Transaction(
            # Criando delay para transações futuras
            timestamp=timestamp or int(time.time()) - 600,
            transaction_id=transaction_id or random.randint(100000, 999999),
            user_id=user_id,
            card_id=card_id or random.randint(100000, 999999),
            site_id=site_id or random.randint(1000, 9999),
            value=value or round(random.uniform(1.0, 1000.0), 2),
            location_id=location or random.randint(1, 100),
            country=country or self._COUNTRIES[user_id % len(self._COUNTRIES)]
        )
        return tx

    def valid_transactions_thread(self) -> None:
        delay = 1 / self._trans_per_sec
        while True:
            tx = self.generate_valid_transaction()
            self._transactions_queue.put(tx)
            time.sleep(delay)

    def generate_high_frequency_fraudulent_transactions(self) -> list[Transaction]:
        tx = self.generate_valid_transaction(
            user_id=random.randint(21000, 29999)
        )
        transactions = []
        for i in range(random.randint(2, 4)):
            # Menos de 5 minutos de diferença
            new_ts = tx.timestamp + (i * random.randint(30, 100))
            transactions.append(
                self.generate_valid_transaction(
                    timestamp=new_ts,
                    user_id=tx.user_id,
                    card_id=tx.card_id
                )
            )
        return transactions

    def generate_high_value_fraudulent_transactions(self) -> list[Transaction]:
        transactions = []
        user_id = random.randint(31000, 39999)
        card_id = None
        ts = int(time.time()) - 3600
        max_value = 0

        for i in range(random.randint(1, 10)):
            tx = self.generate_valid_transaction(
                timestamp=ts + (i * random.randint(360, 600)),
                user_id=user_id,
                card_id=card_id,
            )
            transactions.append(tx)
            max_value = max(max_value, tx.value)
            card_id = tx.value

        transactions.append(
            self.generate_valid_transaction(
                timestamp=ts + 3600,
                user_id=user_id,
                card_id=card_id,
                value=round(max_value * random.uniform(2.1, 5.0), 2)
            )
        )
        return transactions

    def generate_different_country_fraudulent_transactions(self) -> list[Transaction]:
        tx1 = self.generate_valid_transaction()
        tx1.user_id = random.randint(41000, 49999)

        tx2 = self.generate_valid_transaction(
           #  Adiciona ao menos 6 minutos para não gerar conflito com a fraude de frequência
            timestamp=tx1.timestamp + random.randint(360, 600),
            user_id=tx1.user_id,
            card_id=tx1.card_id,
            country=self._COUNTRIES[(tx1.user_id + 1) % len(self._COUNTRIES)]
        )
        return [tx1, tx2]

    def fraudulent_transactions_thread(self, transactions_generator) -> None:
        delay = (1 / self._trans_per_sec) * self._fraudulent_transactions_freq
        while True:
            transactions = transactions_generator()
            for tx in transactions:
                time.sleep(random.uniform(delay, delay * 3))
                self._transactions_queue.put(tx)

    def generate_transactions(self):
        # Transação válidas
        threading.Thread(target=self.valid_transactions_thread,
                         daemon=True).start()

        # Transação fraudulenta: Alta frequência
        threading.Thread(target=self.fraudulent_transactions_thread,
                         args=(self.generate_high_frequency_fraudulent_transactions,),
                         daemon=True).start()

        # Transação fraudulenta: Alto valor
        threading.Thread(target=self.fraudulent_transactions_thread,
                         args=(self.generate_high_value_fraudulent_transactions,),
                         daemon=True).start()

        # Transação fraudulenta - País diferente
        threading.Thread(target=self.fraudulent_transactions_thread,
                         args=(
                         self.generate_different_country_fraudulent_transactions,),
                         daemon=True).start()

        while True:
            transaction = self._transactions_queue.get()
            yield transaction
            self._transactions_queue.task_done()

producer_config = {
    'bootstrap.servers': BROKERS,
    'acks': 'all',
    'retries': 3,
    'batch.size': 16_384,
    'linger.ms': 1000,
    'compression.type': 'gzip',
}

producer = Producer(producer_config)

def send_transaction_to_kafka(transaction: Transaction):
    tx_dict = asdict(transaction)
    tx_json = json.dumps(tx_dict)

    try:
        producer.produce(
            TOPIC,
            key=str(transaction.user_id),  # Envia o user_id como chave para garantir ordenação dentro da mesma partição do tópico
            value=tx_json
        )
        producer.flush()

    except KafkaException as e:
        print(f"Error producing message to Kafka: {e}")
        if e.args[0].code() == KafkaError._ALL_BROKERS_DOWN:
            print("All brokers are down.")
        else:
            print(f"Kafka error code: {e.args[0].code()}")
    except Exception as e:
        print(f"Unexpected error occurred: {e}")

if __name__ == "__main__":
    transaction_generator = TransactionGenerator(trans_per_sec=10)
    count = 0
    try:
        for tx in transaction_generator.generate_transactions():
            count += 1
            send_transaction_to_kafka(tx)
            print(f"Transaction {tx} sent to Kafka.")
    except KeyboardInterrupt:
        print(f"{count} messages generated.")