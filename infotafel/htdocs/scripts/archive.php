<?php
declare(strict_types=1);

header('Content-Type: application/json; charset=utf-8');
header('Cache-Control: no-store, no-cache, must-revalidate, max-age=0');
header('Pragma: no-cache');

require_once __DIR__ . '/helpers.php';

try {
    if (($_SERVER['REQUEST_METHOD'] ?? 'GET') !== 'POST') {
        infotafel_respond(['success' => false, 'error' => 'Nur POST-Anfragen erlaubt.'], 405);
    }

    $input = file_get_contents('php://input');
    $data = [];
    if (is_string($input) && $input !== '') {
        $decoded = json_decode($input, true);
        if (is_array($decoded)) {
            $data = $decoded;
        }
    }
    if (empty($data)) {
        $data = $_POST;
    }

    $monitorId = isset($data['monitor']) ? trim((string) $data['monitor']) : INFOTAFEL_DEFAULT_MONITOR;
    if ($monitorId === '') {
        $monitorId = INFOTAFEL_DEFAULT_MONITOR;
    }

    $monitors = infotafel_get_monitors();
    if (!isset($monitors[$monitorId])) {
        infotafel_respond(['success' => false, 'error' => 'Monitor wurde nicht gefunden.'], 404);
    }

    $anzeige = infotafel_load_json('anzeige.json', []);
    $entry = $anzeige[$monitorId] ?? infotafel_base_display();
    if (empty($entry['text'])) {
        infotafel_respond(['success' => true, 'archived' => false, 'reason' => 'Keine Inhalte vorhanden.']);
    }

    $now = time();
    $expiresAt = isset($entry['expires_at']) ? (int) $entry['expires_at'] : null;
    if ($expiresAt !== null && $expiresAt > $now) {
        infotafel_respond(['success' => false, 'error' => 'Der Inhalt ist noch nicht abgelaufen.'], 409);
    }

    $archiv = infotafel_load_json('archiv.json', []);
    if (!is_array($archiv)) {
        $archiv = [];
    }

    $archiv[] = [
        'monitor' => $monitorId,
        'text' => $entry['text'] ?? '',
        'sopran' => !empty($entry['sopran']),
        'alt' => !empty($entry['alt']),
        'tenor' => !empty($entry['tenor']),
        'bass' => !empty($entry['bass']),
        'updated_at' => $entry['updated_at'] ?? null,
        'expires_at' => $entry['expires_at'] ?? null,
        'archived_at' => date(DATE_ATOM),
    ];
    infotafel_save_json('archiv.json', $archiv);

    $anzeige[$monitorId] = infotafel_base_display();
    infotafel_save_json('anzeige.json', $anzeige);

    infotafel_respond(['success' => true, 'archived' => true]);
} catch (Throwable $e) {
    infotafel_respond([
        'success' => false,
        'error' => 'Interner Fehler: ' . $e->getMessage(),
    ], 500);
}
