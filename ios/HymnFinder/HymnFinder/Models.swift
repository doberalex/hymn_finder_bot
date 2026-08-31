import Foundation

struct Hymn: Codable, Identifiable, Hashable, Sendable {
    let id: String
    let number: Int
    let title: String
    let text: String
    let tune: String
    let words: String
    let songbook: String
    let language: String
    let languageName: String
}

struct Songbook: Identifiable, Hashable {
    var id: String { "\(language)|\(title)" }
    let title: String
    let language: String
    let languageName: String
    let hymnCount: Int
}

enum SearchScope: CaseIterable, Identifiable {
    case all
    case title
    case text

    var id: Self { self }

    @MainActor func label(using language: AppLanguageSettings) -> String {
        switch self {
        case .all: language.text("scope_all")
        case .title: language.text("scope_title")
        case .text: language.text("scope_text")
        }
    }
}
