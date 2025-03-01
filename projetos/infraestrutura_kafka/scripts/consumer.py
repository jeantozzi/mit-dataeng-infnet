from collections import defaultdict
from confluent_kafka import Consumer, Producer
from confluent_kafka.cimpl import TopicPartition
import json

BROKERS = "kafka-broker-1:9092,kafka-broker-2:9092,kafka-broker-3:9092"
INPUT_TOPIC = "transaction"
OUTPUT_TOPIC = "fraudulent-transaction"


# Configuração do Consumer Kafka
consumer = Consumer({
    'bootstrap.servers': BROKERS,
    'group.id': 'consumers',
    'auto.offset.reset': 'earliest',  # Começar a consumir do início
    'enable.auto.commit': True,  # Habilitar auto-commit
    'auto.commit.interval.ms': 2000,  # Commit a cada 2 segundos
    'session.timeout.ms': 10000,  # Timeout de sessão de 10 segundos
    'heartbeat.interval.ms': 3000,  # Intervalo de heartbeat de 3 segundos
    'max.poll.interval.ms': 300_000,    # Tempo máximo entre chamadas sucessivas ao método poll()
})

# Configuração do Producer Kafka
producer_config = {
    'bootstrap.servers': BROKERS,
    'acks': 'all',
    'retries': 3,
    'batch.size': 16_384,
    'linger.ms': 1000,
    'compression.type': 'gzip',
}

# Criar o Producer Kafka com a configuração fornecida
producer = Producer(producer_config)

def on_rebalance(consumer: Consumer, assignment: list[TopicPartition]):
    topics = ", ".join({str(tp.topic) for tp in assignment})
    partitions = ", ".join([str(tp.partition) for tp in assignment])
    print(f"Partitions assignment: Topic {topics}, partitions: {partitions}")

# Estrutura para armazenar transações por usuário
user_transactions = defaultdict(list)
user_last_transaction = {}

# Função para verificar as regras de fraude
def check_fraud(transaction):
    user_id = transaction['user_id']
    timestamp = transaction['timestamp']
    value = transaction['value']
    country = transaction['country']
    card_id = transaction['card_id']

    fraud_alert = None

    # 1. Alta Frequência: Verificar transações dentro de 5 minutos
    if user_id in user_last_transaction:
        last_trans = user_last_transaction[user_id]
        if timestamp - last_trans['timestamp'] < 300:  # 5 minutos
            if value != last_trans['value']:
                fraud_alert = {
                    "timestamp": timestamp,
                    "fraud_type": "Alta Frequência",
                    "user_id": user_id,
                    "card_id": card_id,
                    "details": {
                        "last_transaction_timestamp": last_trans['timestamp'],
                        "current_transaction_timestamp": timestamp,
                        "value_difference": value - last_trans['value']
                    }
                }
                print(f"[FRAUDE - Alta Frequência] Usuário {user_id} fez transações diferentes em menos de 5 minutos.")

    # 2. Alto Valor: Verificar se o valor da transação excede o dobro do maior valor anterior
    if user_id in user_transactions:
        max_value = max([t['value'] for t in user_transactions[user_id]], default=0)
        if value > 2 * max_value:
            fraud_alert = {
                "timestamp": timestamp,
                "fraud_type": "Alto Valor",
                "user_id": user_id,
                "card_id": card_id,
                "details": {
                    "max_previous_value": max_value,
                    "current_value": value
                }
            }
            print(f"[FRAUDE - Alto Valor] Usuário {user_id} fez uma transação de valor {value}, superior ao dobro do maior valor anterior {max_value}.")

    # 3. Outro País: Verificar transações em países diferentes em um intervalo inferior a 2 horas
    if user_id in user_last_transaction:
        last_country = user_last_transaction[user_id]['country']
        last_timestamp = user_last_transaction[user_id]['timestamp']
        if country != last_country and (timestamp - last_timestamp) < 7200:  # 2 horas
            fraud_alert = {
                "timestamp": timestamp,
                "fraud_type": "Outro País",
                "user_id": user_id,
                "card_id": card_id,
                "details": {
                    "last_country": last_country,
                    "current_country": country,
                    "time_difference": timestamp - last_timestamp
                }
            }
            print(f"[FRAUDE - Outro País] Usuário {user_id} fez transações em países diferentes em menos de 2 horas. País atual: {country}, País anterior: {last_country}")

    # Se houver uma fraude, publicar no Kafka
    if fraud_alert:
        # Publicando a fraude com o card_id incluído
        producer.produce(OUTPUT_TOPIC, key=str(user_id), value=json.dumps(fraud_alert))
        producer.flush()  # Garante que a mensagem seja enviada imediatamente

    # Adiciona a transação à lista de transações do usuário
    user_transactions[user_id].append(transaction)
    user_last_transaction[user_id] = transaction

try:
    consumer.subscribe([INPUT_TOPIC], on_assign=on_rebalance)
    print(f"Consuming messages from {INPUT_TOPIC}")
    while True:
        msg = consumer.poll(1.0)
        if msg is None:
            continue
        elif msg.error():
            print(str(msg.error()))
        transaction = json.loads(msg.value())
        if 'user_id' in transaction and 'value' in transaction and 'country' in transaction:
            check_fraud(transaction)

except KeyboardInterrupt:
    print('Encerrando consumidor...')
finally:
    consumer.close()
