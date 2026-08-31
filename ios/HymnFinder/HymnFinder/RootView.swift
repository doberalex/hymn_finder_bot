import SwiftUI

struct RootView: View {
    @EnvironmentObject private var library: HymnLibrary

    var body: some View {
        Group {
            if library.isLoading {
                VStack(spacing: 16) {
                    Image(systemName: "music.note.list")
                        .font(.system(size: 52, weight: .light))
                        .foregroundStyle(Color("AccentColor"))
                    ProgressView("Открываем песенники…")
                }
            } else if let error = library.loadError {
                ContentUnavailableView("Каталог недоступен", systemImage: "exclamationmark.triangle", description: Text(error))
            } else {
                TabView {
                    SearchView()
                        .tabItem { Label("Поиск", systemImage: "magnifyingglass") }
                    SongbooksView()
                        .tabItem { Label("Сборники", systemImage: "books.vertical") }
                    FavoritesView()
                        .tabItem { Label("Избранное", systemImage: "star") }
                    AboutView()
                        .tabItem { Label("Ещё", systemImage: "ellipsis.circle") }
                }
            }
        }
    }
}

struct SearchView: View {
    @EnvironmentObject private var library: HymnLibrary
    @State private var query = ""
    @State private var scope: SearchScope = .all
    @State private var results: [Hymn] = []
    @State private var searchTask: Task<Void, Never>?

    var body: some View {
        NavigationStack {
            Group {
                if query.trimmingCharacters(in: .whitespacesAndNewlines).isEmpty {
                    QuickAccessView()
                } else if results.isEmpty {
                    ContentUnavailableView.search(text: query)
                } else {
                    List(results) { hymn in HymnRow(hymn: hymn) }
                        .listStyle(.plain)
                }
            }
            .navigationTitle("Гимны")
            .searchable(text: $query, placement: .navigationBarDrawer(displayMode: .always), prompt: "Номер, название или текст")
            .searchScopes($scope) {
                ForEach(SearchScope.allCases) { Text($0.rawValue).tag($0) }
            }
            .onChange(of: query) { _, _ in scheduleSearch() }
            .onChange(of: scope) { _, _ in scheduleSearch() }
        }
    }

    private func scheduleSearch() {
        searchTask?.cancel()
        let currentQuery = query
        let currentScope = scope
        searchTask = Task {
            try? await Task.sleep(for: .milliseconds(220))
            guard !Task.isCancelled else { return }
            results = await library.search(currentQuery, scope: currentScope)
        }
    }
}

struct HymnRow: View {
    let hymn: Hymn

    var body: some View {
        NavigationLink {
            HymnDetailView(hymn: hymn)
        } label: {
            VStack(alignment: .leading, spacing: 5) {
                HStack(alignment: .firstTextBaseline) {
                    Text("№ \(hymn.number)").font(.caption.weight(.semibold)).foregroundStyle(.secondary)
                    Text(hymn.title).font(.headline).lineLimit(2)
                }
                Text(hymn.songbook).font(.subheadline).foregroundStyle(.secondary).lineLimit(1)
                if !hymn.text.isEmpty {
                    Text(hymn.text.replacingOccurrences(of: "\n", with: " "))
                        .font(.footnote).foregroundStyle(.secondary).lineLimit(2)
                }
            }.padding(.vertical, 4)
        }
    }
}
