import os
import re
import json
from operator import itemgetter
from collections import Counter


def parse_log(log_line):
    pattern = r'^(.*?) - - \[(.*?)\] "(.*?)" (\d+) (\d+) "(.*?)" "(.*?)" (\d+)$'
    match = re.match(pattern, log_line)
    if match:
        host, timestamp, request_type, status, bytes_sent, referer, user_agent, duration = match.groups()
        return {
            'host': host,
            'timestamp': timestamp,
            'request': request_type,
            'status': status,
            'bytes_sent': bytes_sent,
            'referer': referer,
            'user_agent': user_agent,
            'duration': duration
        }
    else:
        return None


def decode_and_parse_logs(folder_path):
    logs_data = []
    files = os.listdir(folder_path)
    for file_name in files:
        file_path = os.path.join(folder_path, file_name)
        if os.path.isfile(file_path) and file_name.endswith(".log"):
            with open(file_path, 'r', encoding='utf-8') as file:
                for line in file:
                    decoded_line = line.encode('latin1').decode('utf-8')
                    parsed_data = parse_log(decoded_line)
                    if parsed_data:
                        logs_data.append(parsed_data)

    return logs_data


def count_total_requests(logs):
    return len(logs)


def count_requests_by_method(logs):
    methods_count = Counter(log['request'].split(' ')[0] for log in logs)
    return methods_count


def top_3_ip_addresses(logs):
    ip_addresses = [log['host'] for log in logs]
    top_3_ips = Counter(ip_addresses).most_common(3)
    return top_3_ips


def top_3_longest_requests_from_file(logs):
    top_3_requests = sorted(logs, key=itemgetter('duration'), reverse=True)[:3]
    return top_3_requests


def save_statistics_to_json(total_requests, requests_by_method, top_3_ips, top_3_requests):
    statistics = {
        'total_requests': total_requests,
        'requests_by_method': requests_by_method,
        'top_3_ips': top_3_ips,
        'top_3_requests': top_3_requests
    }

    with open('statistics.json', 'w') as file:
        json.dump(statistics, file, indent=4)


def get_script_folder():
    return os.path.dirname(os.path.abspath(__file__))


default_folder_path = get_script_folder()

folder_path_input = input("Введите путь к папке с файлами логов, или оставьте "
                          "поле пустым чтобы использовать путь по умолчанию"
                          "(по умолчанию устанавливается директория в которой находится скрипт): ")
if not folder_path_input:
    folder_path_input = default_folder_path
parsed_logs_data = decode_and_parse_logs(folder_path_input)

total_requests_count = count_total_requests(parsed_logs_data)
print("Общее количество выполненных запросов:", total_requests_count)

requests_by_method_count = count_requests_by_method(parsed_logs_data)
print("Количество запросов по методам:")
for method, count in requests_by_method_count.items():
    print(method, ":", count)

top_3_ips_list = top_3_ip_addresses(parsed_logs_data)
print("Топ 3 IP-адресов:")
for ip, count in top_3_ips_list:
    print(ip, ":", count)
    print("---------------------------")

top_3_requests_list = top_3_longest_requests_from_file(parsed_logs_data)
print("Топ 3 самых долгих запросов:")
for request_entry in top_3_requests_list:
    print("Метод:", request_entry['request'].split(' ')[0])
    print("URL:", request_entry['request'].split(' ')[1])
    print("IP:", request_entry['host'])
    print("Длительность:", request_entry['duration'])
    print("Дата и время запроса:", request_entry['timestamp'])
    print("-------------------------------------------------------")

save_statistics_to_json(total_requests_count, requests_by_method_count, top_3_ips_list, top_3_requests_list)
