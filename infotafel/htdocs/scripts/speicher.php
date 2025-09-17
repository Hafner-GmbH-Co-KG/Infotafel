<?php
declare(strict_types=1);

header('Content-Type: application/json; charset=utf-8');
header('Cache-Control: no-store, no-cache, must-revalidate, max-age=0');
header('Pragma: no-cache');

require_once __DIR__ . '/helpers.php';

try {
    $method = $_SERVER['REQUEST_METHOD'] ?? 'GET';
    $input = file_get_contents('php://input');
    $data = [];
    if (is_string($input) && $input !== '') {
        $decoded = json_decode($input, true);
        if (is_array($decoded)) {
            $data = $decoded;
        }
    }
    if ($method === 'POST' && empty($data)) {
        $data = $_POST;
    }

    $action = $data['action'] ?? $_GET['action'] ?? null;
    if ($action === null) {
        $action = $method === 'GET' ? 'getMonitors' : 'saveDisplay';
    }

    switch ($action) {
        case 'getMonitors':
            handle_get_monitors();
            break;
        case 'getDisplay':
            handle_get_display($data);
            break;
        case 'saveDisplay':
            if ($method !== 'POST') {
                infotafel_respond(['success' => false, 'error' => 'Nur POST-Anfragen erlaubt.'], 405);
            }
            handle_save_display($data);
            break;
        case 'createMonitor':
            if ($method !== 'POST') {
                infotafel_respond(['success' => false, 'error' => 'Nur POST-Anfragen erlaubt.'], 405);
            }
            handle_create_monitor($data);
            break;
        case 'deleteMonitor':
            if ($method !== 'POST') {
                infotafel_respond(['success' => false, 'error' => 'Nur POST-Anfragen erlaubt.'], 405);
            }
            handle_delete_monitor($data);
            break;
        default:
            infotafel_respond(['success' => false, 'error' => 'Unbekannte Aktion.'], 400);
    }
} catch (Throwable $e) {
    infotafel_respond([
        'success' => false,
        'error' => 'Interner Fehler: ' . $e->getMessage(),
    ], 500);
}

function handle_get_monitors(): void
{
    $monitors = infotafel_get_monitors();
    $anzeige = infotafel_load_json('anzeige.json', []);
    $response = [];
    foreach ($monitors as $id => $monitor) {
        $display = $anzeige[$id] ?? infotafel_base_display();
        $response[] = [
            'id' => $id,
            'name' => $monitor['name'] ?? $id,
            'slug' => $monitor['slug'] ?? null,
            'created_at' => $monitor['created_at'] ?? null,
            'share_path' => infotafel_share_path($id),
            'has_active_content' => !empty($display['text']),
        ];
    }

    usort($response, static function ($a, $b) {
        if ($a['id'] === INFOTAFEL_DEFAULT_MONITOR) {
            return -1;
        }
        if ($b['id'] === INFOTAFEL_DEFAULT_MONITOR) {
            return 1;
        }
        return strcmp((string) $a['name'], (string) $b['name']);
    });

    infotafel_respond(['success' => true, 'monitors' => $response]);
}

function handle_get_display(array $data): void
{
    $monitorId = $data['monitor'] ?? $_GET['monitor'] ?? INFOTAFEL_DEFAULT_MONITOR;
    $monitorId = is_string($monitorId) ? trim($monitorId) : INFOTAFEL_DEFAULT_MONITOR;
    $monitors = infotafel_get_monitors();
    if (!isset($monitors[$monitorId])) {
        infotafel_respond(['success' => false, 'error' => 'Monitor wurde nicht gefunden.'], 404);
    }

    $anzeige = infotafel_load_json('anzeige.json', []);
    $display = $anzeige[$monitorId] ?? infotafel_base_display();
    $settings = infotafel_load_json('einstellungen.json', []);
    $duration = $settings[$monitorId]['anzeigedauer'] ?? INFOTAFEL_DEFAULT_DURATION;

    infotafel_respond([
        'success' => true,
        'monitor' => [
            'id' => $monitorId,
            'name' => $monitors[$monitorId]['name'] ?? $monitorId,
            'share_path' => infotafel_share_path($monitorId),
            'display' => $display,
            'settings' => ['anzeigedauer' => $duration],
        ],
    ]);
}

function handle_save_display(array $data): void
{
    $monitorId = $data['monitor'] ?? INFOTAFEL_DEFAULT_MONITOR;
    if (!is_string($monitorId) || trim($monitorId) === '') {
        infotafel_respond(['success' => false, 'error' => 'Monitor-ID fehlt.'], 400);
    }
    $monitorId = trim($monitorId);
    $monitors = infotafel_get_monitors();
    if (!isset($monitors[$monitorId])) {
        infotafel_respond(['success' => false, 'error' => 'Monitor wurde nicht gefunden.'], 404);
    }

    $text = isset($data['text']) ? trim((string) $data['text']) : '';
    $duration = isset($data['duration']) ? (int) $data['duration'] : INFOTAFEL_DEFAULT_DURATION;
    if ($duration < 0) {
        $duration = INFOTAFEL_DEFAULT_DURATION;
    }
    $expireAt = $duration > 0 ? time() + $duration : null;

    $entry = [
        'text' => $text,
        'sopran' => !empty($data['sopran']),
        'alt' => !empty($data['alt']),
        'tenor' => !empty($data['tenor']),
        'bass' => !empty($data['bass']),
        'updated_at' => date(DATE_ATOM),
        'expires_at' => $expireAt,
    ];

    $anzeige = infotafel_load_json('anzeige.json', []);
    $anzeige[$monitorId] = $entry;
    infotafel_save_json('anzeige.json', $anzeige);

    $settings = infotafel_load_json('einstellungen.json', []);
    $settings[$monitorId] = ['anzeigedauer' => $duration];
    infotafel_save_json('einstellungen.json', $settings);

    infotafel_respond(['success' => true, 'monitor' => $monitorId]);
}

function handle_create_monitor(array $data): void
{
    $token = $data['token'] ?? '';
    if (!is_string($token) || $token !== INFOTAFEL_ADMIN_TOKEN) {
        infotafel_respond(['success' => false, 'error' => 'Ungültiger Admin-Token.'], 403);
    }

    $name = isset($data['name']) ? trim((string) $data['name']) : '';
    if ($name === '') {
        infotafel_respond(['success' => false, 'error' => 'Der Name darf nicht leer sein.'], 400);
    }

    $monitors = infotafel_get_monitors();
    $existingIds = array_keys($monitors);
    $slug = infotafel_slugify($name);
    if ($slug === '') {
        $slug = 'monitor';
    }

    $candidate = $slug;
    $suffix = 2;
    while (in_array($candidate, $existingIds, true)) {
        $candidate = $slug . '-' . $suffix;
        $suffix++;
    }
    $monitorId = $candidate;

    $monitors[$monitorId] = [
        'id' => $monitorId,
        'name' => $name,
        'slug' => $monitorId,
        'created_at' => date(DATE_ATOM),
    ];
    infotafel_save_monitors($monitors);

    $anzeige = infotafel_load_json('anzeige.json', []);
    $anzeige[$monitorId] = infotafel_base_display();
    infotafel_save_json('anzeige.json', $anzeige);

    $settings = infotafel_load_json('einstellungen.json', []);
    $settings[$monitorId] = ['anzeigedauer' => INFOTAFEL_DEFAULT_DURATION];
    infotafel_save_json('einstellungen.json', $settings);

    infotafel_respond([
        'success' => true,
        'monitor' => [
            'id' => $monitorId,
            'name' => $name,
            'share_path' => infotafel_share_path($monitorId),
        ],
    ]);
}

function handle_delete_monitor(array $data): void
{
    $token = $data['token'] ?? '';
    if (!is_string($token) || $token !== INFOTAFEL_ADMIN_TOKEN) {
        infotafel_respond(['success' => false, 'error' => 'Ungültiger Admin-Token.'], 403);
    }

    $monitorId = isset($data['monitor']) ? trim((string) $data['monitor']) : '';
    if ($monitorId === '') {
        infotafel_respond(['success' => false, 'error' => 'Monitor-ID fehlt.'], 400);
    }
    if ($monitorId === INFOTAFEL_DEFAULT_MONITOR) {
        infotafel_respond(['success' => false, 'error' => 'Der Standardmonitor kann nicht gelöscht werden.'], 400);
    }

    $monitors = infotafel_get_monitors();
    if (!isset($monitors[$monitorId])) {
        infotafel_respond(['success' => false, 'error' => 'Monitor wurde nicht gefunden.'], 404);
    }
    unset($monitors[$monitorId]);
    infotafel_save_monitors($monitors);

    $anzeige = infotafel_load_json('anzeige.json', []);
    unset($anzeige[$monitorId]);
    infotafel_save_json('anzeige.json', $anzeige);

    $settings = infotafel_load_json('einstellungen.json', []);
    unset($settings[$monitorId]);
    infotafel_save_json('einstellungen.json', $settings);

    infotafel_respond(['success' => true, 'monitor' => $monitorId]);
}
