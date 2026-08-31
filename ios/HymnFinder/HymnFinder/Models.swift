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

enum SearchScope: String, CaseIterable, Identifiable {
    case all = "Все"
    case title = "Название"
    case text = "Текст"

    var id: Self { self }
}
