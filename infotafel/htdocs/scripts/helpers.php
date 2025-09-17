<?php
declare(strict_types=1);

require_once __DIR__ . '/../config.php';

function infotafel_data_dir(): string
{
    static $dir = null;
    if ($dir === null) {
        $candidate = realpath(__DIR__ . '/../data');
        if ($candidate === false) {
            $candidate = __DIR__ . '/../data';
        }
        $dir = $candidate;
    }
    return $dir;
}

function infotafel_require_data_dir(): void
{
    $dir = infotafel_data_dir();
    if (!is_dir($dir)) {
        throw new RuntimeException('Datenverzeichnis konnte nicht gefunden werden.');
    }
}

function infotafel_load_json(string $filename, $default = [])
{
    infotafel_require_data_dir();
    $path = infotafel_data_dir() . '/' . $filename;
    if (!is_file($path)) {
        return $default;
    }
    $raw = file_get_contents($path);
    if ($raw === false) {
        return $default;
    }
    $decoded = json_decode($raw, true);
    if ($decoded === null && json_last_error() !== JSON_ERROR_NONE) {
        return $default;
    }
    return $decoded;
}

function infotafel_save_json(string $filename, $data): void
{
    infotafel_require_data_dir();
    $path = infotafel_data_dir() . '/' . $filename;
    $encoded = json_encode($data, JSON_PRETTY_PRINT | JSON_UNESCAPED_UNICODE);
    if ($encoded === false) {
        throw new RuntimeException('JSON konnte nicht kodiert werden.');
    }
    $result = file_put_contents($path, $encoded . "\n", LOCK_EX);
    if ($result === false) {
        throw new RuntimeException('Datei ' . $filename . ' konnte nicht gespeichert werden.');
    }
}

function infotafel_base_display(): array
{
    return [
        'text' => '',
        'sopran' => false,
        'alt' => false,
        'tenor' => false,
        'bass' => false,
        'updated_at' => null,
        'expires_at' => null,
    ];
}

function infotafel_slugify(string $text): string
{
    $text = trim($text);
    if ($text === '') {
        return '';
    }
    $text = iconv('UTF-8', 'ASCII//TRANSLIT', $text);
    $text = strtolower((string) $text);
    $text = preg_replace('/[^a-z0-9]+/', '-', $text);
    $text = trim($text ?? '', '-');
    return $text ?? '';
}

function infotafel_get_monitors(): array
{
    $raw = infotafel_load_json('monitors.json', []);
    $monitors = [];
    if (is_array($raw)) {
        foreach ($raw as $monitor) {
            if (is_array($monitor) && isset($monitor['id'])) {
                $monitors[(string) $monitor['id']] = $monitor;
            }
        }
    }

    $changed = false;
    if (!isset($monitors[INFOTAFEL_DEFAULT_MONITOR])) {
        $monitors[INFOTAFEL_DEFAULT_MONITOR] = [
            'id' => INFOTAFEL_DEFAULT_MONITOR,
            'name' => INFOTAFEL_DEFAULT_MONITOR_NAME,
            'slug' => infotafel_slugify(INFOTAFEL_DEFAULT_MONITOR_NAME) ?: INFOTAFEL_DEFAULT_MONITOR,
            'created_at' => date(DATE_ATOM),
        ];
        $changed = true;
    }

    if ($changed) {
        infotafel_save_monitors($monitors);
        $anzeige = infotafel_load_json('anzeige.json', []);
        if (!isset($anzeige[INFOTAFEL_DEFAULT_MONITOR])) {
            $anzeige[INFOTAFEL_DEFAULT_MONITOR] = infotafel_base_display();
            infotafel_save_json('anzeige.json', $anzeige);
        }
        $settings = infotafel_load_json('einstellungen.json', []);
        if (!isset($settings[INFOTAFEL_DEFAULT_MONITOR])) {
            $settings[INFOTAFEL_DEFAULT_MONITOR] = ['anzeigedauer' => INFOTAFEL_DEFAULT_DURATION];
            infotafel_save_json('einstellungen.json', $settings);
        }
    }

    return $monitors;
}

function infotafel_save_monitors(array $monitors): void
{
    infotafel_save_json('monitors.json', array_values($monitors));
}

function infotafel_share_path(string $monitorId): string
{
    return 'index.html?monitor=' . rawurlencode($monitorId);
}

function infotafel_respond(array $payload, int $status = 200): void
{
    http_response_code($status);
    echo json_encode($payload, JSON_PRETTY_PRINT | JSON_UNESCAPED_UNICODE);
    exit;
}
