import Foundation

enum InterfaceLanguage: String, CaseIterable, Identifiable {
    case ru, uk, en, uz

    var id: String { rawValue }
    var locale: Locale { Locale(identifier: rawValue) }

    var nativeName: String {
        switch self {
        case .ru: "Русский"
        case .uk: "Українська"
        case .en: "English"
        case .uz: "O‘zbekcha"
        }
    }

    static var system: InterfaceLanguage {
        let preferred = Locale.preferredLanguages.first?.lowercased() ?? "ru"
        return allCases.first { preferred.hasPrefix($0.rawValue) } ?? .ru
    }
}

@MainActor
final class AppLanguageSettings: ObservableObject {
    static let systemValue = "system"

    @Published var selection: String {
        didSet { UserDefaults.standard.set(selection, forKey: "appLanguage") }
    }

    init() {
        let saved = UserDefaults.standard.string(forKey: "appLanguage") ?? Self.systemValue
        selection = saved == Self.systemValue || InterfaceLanguage(rawValue: saved) != nil ? saved : Self.systemValue
    }

    var resolved: InterfaceLanguage {
        selection == Self.systemValue ? .system : InterfaceLanguage(rawValue: selection) ?? .system
    }

    func text(_ key: String) -> String {
        Self.translations[resolved]?[key] ?? Self.translations[.ru]?[key] ?? key
    }

    func format(_ key: String, _ arguments: CVarArg...) -> String {
        String(format: text(key), locale: resolved.locale, arguments: arguments)
    }

    func languageName(_ code: String) -> String {
        InterfaceLanguage(rawValue: code)?.nativeName ?? code.uppercased()
    }

    var systemOptionTitle: String {
        "\(text("system_language")) (\(InterfaceLanguage.system.nativeName))"
    }

    private static let translations: [InterfaceLanguage: [String: String]] = [
        .ru: [
            "loading": "Открываем песенники…", "catalog_unavailable": "Каталог недоступен",
            "search": "Поиск", "songbooks": "Сборники", "favorites": "Избранное", "more": "Ещё",
            "hymns": "Гимны", "search_prompt": "Номер, название или текст", "nothing_found": "Ничего не найдено",
            "scope_all": "Все", "scope_title": "Название", "scope_text": "Текст",
            "songbook_search": "Название сборника", "number_or_text": "Номер или текст", "songs_count": "%d песен",
            "remove_quick": "Убрать из быстрого доступа", "add_quick": "Добавить в быстрый доступ",
            "empty": "Пока пусто", "favorites_hint": "Добавляйте часто используемые гимны в избранное",
            "smaller": "Меньше", "larger": "Больше", "version": "Версия", "offline": "Работа без интернета", "yes": "Да",
            "about": "О приложении", "tip": "Подсказка", "privacy": "Конфиденциальность",
            "tip_text": "Ищите по номеру, названию или нескольким словам из любого куплета. Размер текста меняется кнопкой Aa в открытом гимне.",
            "privacy_text": "Поисковые запросы и избранное остаются на этом устройстве. Приложение не требует регистрации.",
            "quick_access": "Быстрый доступ", "quick_subtitle": "Откройте любимый сборник или выберите язык", "by_language": "По языку",
            "pin_hint": "Закрепите сборник кнопкой булавки на его странице", "app_language": "Язык приложения",
            "language": "Язык", "system_language": "Системный"
        ],
        .uk: [
            "loading": "Відкриваємо пісенники…", "catalog_unavailable": "Каталог недоступний",
            "search": "Пошук", "songbooks": "Збірники", "favorites": "Обране", "more": "Ще",
            "hymns": "Гімни", "search_prompt": "Номер, назва або текст", "nothing_found": "Нічого не знайдено",
            "scope_all": "Усі", "scope_title": "Назва", "scope_text": "Текст",
            "songbook_search": "Назва збірника", "number_or_text": "Номер або текст", "songs_count": "%d пісень",
            "remove_quick": "Прибрати зі швидкого доступу", "add_quick": "Додати до швидкого доступу",
            "empty": "Поки порожньо", "favorites_hint": "Додавайте часто використовувані гімни до обраного",
            "smaller": "Менше", "larger": "Більше", "version": "Версія", "offline": "Робота без інтернету", "yes": "Так",
            "about": "Про застосунок", "tip": "Підказка", "privacy": "Конфіденційність",
            "tip_text": "Шукайте за номером, назвою або кількома словами з будь-якого куплета. Розмір тексту змінюється кнопкою Aa у відкритому гімні.",
            "privacy_text": "Пошукові запити й обране залишаються на цьому пристрої. Застосунок не потребує реєстрації.",
            "quick_access": "Швидкий доступ", "quick_subtitle": "Відкрийте улюблений збірник або виберіть мову", "by_language": "За мовою",
            "pin_hint": "Закріпіть збірник кнопкою-шпилькою на його сторінці", "app_language": "Мова застосунку",
            "language": "Мова", "system_language": "Системна"
        ],
        .en: [
            "loading": "Opening hymnals…", "catalog_unavailable": "Catalog unavailable",
            "search": "Search", "songbooks": "Hymnals", "favorites": "Favorites", "more": "More",
            "hymns": "Hymns", "search_prompt": "Number, title, or lyrics", "nothing_found": "No results found",
            "scope_all": "All", "scope_title": "Title", "scope_text": "Lyrics",
            "songbook_search": "Hymnal name", "number_or_text": "Number or lyrics", "songs_count": "%d hymns",
            "remove_quick": "Remove from Quick Access", "add_quick": "Add to Quick Access",
            "empty": "Nothing here yet", "favorites_hint": "Add frequently used hymns to Favorites",
            "smaller": "Smaller", "larger": "Larger", "version": "Version", "offline": "Works offline", "yes": "Yes",
            "about": "About", "tip": "Tip", "privacy": "Privacy",
            "tip_text": "Search by number, title, or a few words from any verse. Change the text size with the Aa button in an open hymn.",
            "privacy_text": "Search queries and favorites stay on this device. No account is required.",
            "quick_access": "Quick Access", "quick_subtitle": "Open a favorite hymnal or choose a language", "by_language": "By language",
            "pin_hint": "Pin a hymnal from its page to add it here", "app_language": "App language",
            "language": "Language", "system_language": "System"
        ],
        .uz: [
            "loading": "Qo‘shiq to‘plamlari ochilmoqda…", "catalog_unavailable": "Katalog mavjud emas",
            "search": "Qidiruv", "songbooks": "To‘plamlar", "favorites": "Tanlangan", "more": "Yana",
            "hymns": "Madhiyalar", "search_prompt": "Raqam, nom yoki matn", "nothing_found": "Hech narsa topilmadi",
            "scope_all": "Barchasi", "scope_title": "Nomi", "scope_text": "Matn",
            "songbook_search": "To‘plam nomi", "number_or_text": "Raqam yoki matn", "songs_count": "%d qo‘shiq",
            "remove_quick": "Tezkor kirishdan olib tashlash", "add_quick": "Tezkor kirishga qo‘shish",
            "empty": "Hozircha bo‘sh", "favorites_hint": "Ko‘p ishlatiladigan madhiyalarni tanlanganga qo‘shing",
            "smaller": "Kichikroq", "larger": "Kattaroq", "version": "Versiya", "offline": "Internetsiz ishlaydi", "yes": "Ha",
            "about": "Ilova haqida", "tip": "Maslahat", "privacy": "Maxfiylik",
            "tip_text": "Raqam, nom yoki istalgan banddagi bir necha so‘z orqali qidiring. Ochiq madhiyada Aa tugmasi bilan matn o‘lchamini o‘zgartiring.",
            "privacy_text": "Qidiruvlar va tanlanganlar shu qurilmada qoladi. Ro‘yxatdan o‘tish talab qilinmaydi.",
            "quick_access": "Tezkor kirish", "quick_subtitle": "Sevimli to‘plamni oching yoki tilni tanlang", "by_language": "Til bo‘yicha",
            "pin_hint": "To‘plam sahifasidagi qadag‘ich tugmasi bilan uni bu yerga qo‘shing", "app_language": "Ilova tili",
            "language": "Til", "system_language": "Tizim tili"
        ]
    ]
}
