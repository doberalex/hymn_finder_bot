import Foundation
import SwiftUI

@MainActor
final class HymnLibrary: ObservableObject {
    @Published private(set) var hymns: [Hymn] = []
    @Published private(set) var isLoading = true
    @Published private(set) var loadError: String?
    @AppStorage("favoriteHymnIDs") private var favoriteData = ""
    @AppStorage("quickSongbookIDs") private var quickSongbookData = ""
    @AppStorage("quickSongbooksInitialized") private var quickSongbooksInitialized = false

    private static let defaultQuickSongbookIDs = [
        "ru|Песнь Воз. Совета Церквей",
        "ru|Молодежный сборник"
    ]

    private(set) lazy var songbooks: [Songbook] = {
        let grouped = Dictionary(grouping: hymns) { "\($0.language)|\($0.songbook)" }
        return grouped.values.compactMap { group in
            guard let first = group.first else { return nil }
            return Songbook(
                title: first.songbook,
                language: first.language,
                languageName: first.languageName,
                hymnCount: group.count
            )
        }.sorted {
            if $0.languageName != $1.languageName {
                return $0.languageName.localizedStandardCompare($1.languageName) == .orderedAscending
            }
            return $0.title.localizedStandardCompare($1.title) == .orderedAscending
        }
    }()

    init() {
        if !quickSongbooksInitialized {
            quickSongbookData = Self.defaultQuickSongbookIDs.joined(separator: "\n")
            quickSongbooksInitialized = true
        }
        Task { await load() }
    }

    func load() async {
        do {
            guard let url = Bundle.main.url(forResource: "hymns", withExtension: "json") else {
                throw CocoaError(.fileNoSuchFile)
            }
            let decoded = try await Task.detached(priority: .userInitiated) {
                let data = try Data(contentsOf: url, options: .mappedIfSafe)
                return try JSONDecoder().decode([Hymn].self, from: data)
            }.value
            hymns = decoded
            isLoading = false
        } catch {
            loadError = "Не удалось открыть каталог гимнов. \(error.localizedDescription)"
            isLoading = false
        }
    }

    func search(_ query: String, scope: SearchScope, songbookID: String? = nil, limit: Int = 100) async -> [Hymn] {
        let snapshot = hymns
        return await Task.detached(priority: .userInitiated) {
            let filteredBook = songbookID.map { id in
                snapshot.filter { "\($0.language)|\($0.songbook)" == id }
            } ?? snapshot
            let needle = query.searchNormalized
            guard !needle.isEmpty else { return Array(filteredBook.prefix(limit)) }

            if let number = Int(needle) {
                return Array(filteredBook.filter { $0.number == number }.prefix(limit))
            }

            return Array(filteredBook.lazy.filter { hymn in
                switch scope {
                case .all:
                    return hymn.title.searchNormalized.contains(needle) || hymn.text.searchNormalized.contains(needle)
                case .title:
                    return hymn.title.searchNormalized.contains(needle)
                case .text:
                    return hymn.text.searchNormalized.contains(needle)
                }
            }.prefix(limit))
        }.value
    }

    var favorites: [Hymn] {
        let ids = favoriteIDs
        return hymns.filter { ids.contains($0.id) }
    }

    func isFavorite(_ hymn: Hymn) -> Bool { favoriteIDs.contains(hymn.id) }

    func toggleFavorite(_ hymn: Hymn) {
        var ids = favoriteIDs
        if ids.contains(hymn.id) { ids.remove(hymn.id) } else { ids.insert(hymn.id) }
        favoriteData = ids.sorted().joined(separator: "\n")
        objectWillChange.send()
    }

    private var favoriteIDs: Set<String> {
        Set(favoriteData.split(separator: "\n").map(String.init))
    }

    var quickSongbooks: [Songbook] {
        let booksByID = Dictionary(uniqueKeysWithValues: songbooks.map { ($0.id, $0) })
        return quickSongbookIDs.compactMap { booksByID[$0] }
    }

    func isQuickAccess(_ songbook: Songbook) -> Bool {
        quickSongbookIDs.contains(songbook.id)
    }

    func toggleQuickAccess(_ songbook: Songbook) {
        var ids = quickSongbookIDs
        if let index = ids.firstIndex(of: songbook.id) {
            ids.remove(at: index)
        } else {
            ids.append(songbook.id)
        }
        quickSongbookData = ids.joined(separator: "\n")
        objectWillChange.send()
    }

    private var quickSongbookIDs: [String] {
        quickSongbookData.split(separator: "\n").map(String.init)
    }
}

private extension String {
    var searchNormalized: String {
        folding(options: [.caseInsensitive, .diacriticInsensitive], locale: .current)
            .components(separatedBy: CharacterSet.alphanumerics.inverted)
            .filter { !$0.isEmpty }
            .joined(separator: " ")
    }
}
