<?php
// Runs inside the Snipe-IT image via `artisan tinker`: creates settings, an admin and an API token.
use App\Models\Setting;
use App\Models\User;
use Illuminate\Support\Facades\Artisan;
use Illuminate\Support\Facades\Hash;

if (Setting::count() === 0) {
    $s = new Setting();
    $s->forceFill([
        'site_name' => 'Snipe-IT Testing',
        'alert_email' => 'admin@example.com',
        'locale' => 'en-US',
        'brand' => 1,
        'default_currency' => 'EUR',
        'per_page' => 50,
        'email_domain' => 'example.com',
        'email_format' => 'filastname',
        'username_format' => 'filastname',
        'auto_increment_assets' => 0,
        'auto_increment_prefix' => '',
        'next_auto_tag_base' => 1,
        'modellist_displays' => 'image,category,manufacturer,model_number',
        'login_note' => '',
    ])->save();
}

$admin = User::where('username', 'admin')->first();
if (!$admin) {
    $admin = new User();
    $admin->forceFill([
        'first_name' => 'Admin',
        'last_name' => 'Testing',
        'username' => 'admin',
        'email' => 'admin@example.com',
        'password' => Hash::make(getenv('SEED_ADMIN_PASSWORD') ?: 'admin-Passw0rd-123!'),
        'activated' => 1,
        'permissions' => '{"superuser":"1"}',
    ])->save();
}

if (!is_file('/shared/token')) {
    try {
        $token = $admin->createToken('testing-seed')->accessToken;
    } catch (\RuntimeException $e) {
        // Passport has no personal access client yet
        Artisan::call('passport:client', ['--personal' => true, '--name' => 'Testing', '--no-interaction' => true]);
        $token = $admin->createToken('testing-seed')->accessToken;
    }
    file_put_contents('/shared/token', $token);
}
echo "bootstrap done\n";
