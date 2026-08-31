import SwiftUI

private struct LanguageShortcut: Identifiable {
    let id: String
    let title: String
    let flag: FlagKind
}

private enum FlagKind {
    case russia, ukraine, unitedKingdom, uzbekistan
}

struct QuickAccessView: View {
    @EnvironmentObject private var library: HymnLibrary

    private let languages = [
        LanguageShortcut(id: "ru", title: "Русский", flag: .russia),
        LanguageShortcut(id: "uk", title: "Українська", flag: .ukraine),
        LanguageShortcut(id: "en", title: "English", flag: .unitedKingdom),
        LanguageShortcut(id: "uz", title: "O‘zbekcha", flag: .uzbekistan)
    ]

    var body: some View {
        ScrollView {
            VStack(alignment: .leading, spacing: 24) {
                VStack(alignment: .leading, spacing: 5) {
                    Text("Быстрый доступ").font(.title2.bold())
                    Text("Откройте любимый сборник или выберите язык")
                        .font(.subheadline).foregroundStyle(.secondary)
                }

                VStack(spacing: 12) {
                    quickSongbook(
                        storedTitle: "Песнь Воз. Совета Церквей",
                        displayTitle: "Песнь Возрождения Совета Церквей",
                        icon: "music.note.list"
                    )
                    quickSongbook(
                        storedTitle: "Молодежный сборник",
                        displayTitle: "Молодёжный сборник",
                        icon: "person.3.fill"
                    )
                }

                VStack(alignment: .leading, spacing: 12) {
                    Text("По языку").font(.headline)
                    LazyVGrid(columns: [GridItem(.flexible()), GridItem(.flexible())], spacing: 12) {
                        ForEach(languages) { language in
                            NavigationLink {
                                LanguageSongbooksView(languageCode: language.id, title: language.title)
                            } label: {
                                LanguageCard(shortcut: language)
                            }
                            .buttonStyle(.plain)
                        }
                    }
                }
            }
            .padding(.horizontal)
            .padding(.top, 26)
            .padding(.bottom, 28)
        }
    }

    @ViewBuilder
    private func quickSongbook(storedTitle: String, displayTitle: String, icon: String) -> some View {
        if let songbook = library.songbooks.first(where: { $0.title == storedTitle }) {
            NavigationLink {
                SongbookDetailView(songbook: songbook)
            } label: {
                QuickSongbookCard(songbook: songbook, displayTitle: displayTitle, icon: icon)
            }
            .buttonStyle(.plain)
        }
    }
}

private struct QuickSongbookCard: View {
    let songbook: Songbook
    let displayTitle: String
    let icon: String

    var body: some View {
        HStack(alignment: .bottom, spacing: 16) {
            VStack(alignment: .leading, spacing: 8) {
                Text(displayTitle).font(.headline).multilineTextAlignment(.leading)
                Text("\(songbook.hymnCount) песен")
                    .font(.subheadline).foregroundStyle(.secondary)
            }
            Spacer(minLength: 8)
            Image(systemName: icon)
                .font(.system(size: 28, weight: .semibold))
                .foregroundStyle(Color("AccentColor"))
                .accessibilityHidden(true)
        }
        .frame(maxWidth: .infinity, minHeight: 78, alignment: .leading)
        .padding(18)
        .background(.regularMaterial, in: RoundedRectangle(cornerRadius: 20, style: .continuous))
        .overlay {
            RoundedRectangle(cornerRadius: 20, style: .continuous)
                .stroke(.primary.opacity(0.08), lineWidth: 1)
        }
        .contentShape(RoundedRectangle(cornerRadius: 20, style: .continuous))
    }
}

private struct LanguageCard: View {
    let shortcut: LanguageShortcut

    var body: some View {
        ZStack(alignment: .bottomLeading) {
            FlagBackdrop(kind: shortcut.flag)
            LinearGradient(colors: [.clear, .black.opacity(0.72)], startPoint: .top, endPoint: .bottom)
            HStack(alignment: .bottom) {
                Text(shortcut.title)
                    .font(.headline).foregroundStyle(.white).lineLimit(1).minimumScaleFactor(0.8)
                Spacer(minLength: 4)
                Image(systemName: "chevron.right")
                    .font(.caption.bold()).foregroundStyle(.white.opacity(0.8))
            }.padding(14)
        }
        .frame(height: 112)
        .clipShape(RoundedRectangle(cornerRadius: 20, style: .continuous))
        .overlay {
            RoundedRectangle(cornerRadius: 20, style: .continuous)
                .stroke(.primary.opacity(0.08), lineWidth: 1)
        }
        .accessibilityElement(children: .combine)
        .accessibilityLabel(shortcut.title)
    }
}

private struct FlagBackdrop: View {
    let kind: FlagKind

    var body: some View {
        Canvas { context, size in
            let rect = CGRect(origin: .zero, size: size)
            context.fill(Path(rect), with: .color(Color(white: 0.72)))

            switch kind {
            case .russia:
                stripe(&context, rect: CGRect(x: 0, y: 0, width: size.width, height: size.height / 3), shade: 0.9)
                stripe(&context, rect: CGRect(x: 0, y: size.height / 3, width: size.width, height: size.height / 3), shade: 0.58)
                stripe(&context, rect: CGRect(x: 0, y: size.height * 2 / 3, width: size.width, height: size.height / 3), shade: 0.32)
            case .ukraine:
                stripe(&context, rect: CGRect(x: 0, y: 0, width: size.width, height: size.height / 2), shade: 0.36)
                stripe(&context, rect: CGRect(x: 0, y: size.height / 2, width: size.width, height: size.height / 2), shade: 0.76)
            case .unitedKingdom:
                stripe(&context, rect: rect, shade: 0.28)
                diagonal(&context, size: size, from: CGPoint(x: 0, y: 0), to: CGPoint(x: size.width, y: size.height), width: 21, shade: 0.86)
                diagonal(&context, size: size, from: CGPoint(x: size.width, y: 0), to: CGPoint(x: 0, y: size.height), width: 21, shade: 0.86)
                diagonal(&context, size: size, from: CGPoint(x: 0, y: 0), to: CGPoint(x: size.width, y: size.height), width: 8, shade: 0.52)
                diagonal(&context, size: size, from: CGPoint(x: size.width, y: 0), to: CGPoint(x: 0, y: size.height), width: 8, shade: 0.52)
                stripe(&context, rect: CGRect(x: size.width * 0.39, y: 0, width: size.width * 0.22, height: size.height), shade: 0.9)
                stripe(&context, rect: CGRect(x: 0, y: size.height * 0.34, width: size.width, height: size.height * 0.32), shade: 0.9)
                stripe(&context, rect: CGRect(x: size.width * 0.44, y: 0, width: size.width * 0.12, height: size.height), shade: 0.45)
                stripe(&context, rect: CGRect(x: 0, y: size.height * 0.42, width: size.width, height: size.height * 0.16), shade: 0.45)
            case .uzbekistan:
                stripe(&context, rect: CGRect(x: 0, y: 0, width: size.width, height: size.height * 0.32), shade: 0.42)
                stripe(&context, rect: CGRect(x: 0, y: size.height * 0.35, width: size.width, height: size.height * 0.3), shade: 0.9)
                stripe(&context, rect: CGRect(x: 0, y: size.height * 0.68, width: size.width, height: size.height * 0.32), shade: 0.58)
                stripe(&context, rect: CGRect(x: 0, y: size.height * 0.32, width: size.width, height: size.height * 0.03), shade: 0.18)
                stripe(&context, rect: CGRect(x: 0, y: size.height * 0.65, width: size.width, height: size.height * 0.03), shade: 0.18)
                let moon = Path(ellipseIn: CGRect(x: 15, y: 13, width: 28, height: 28))
                context.fill(moon, with: .color(.white.opacity(0.9)))
                let cutout = Path(ellipseIn: CGRect(x: 22, y: 11, width: 27, height: 27))
                context.fill(cutout, with: .color(Color(white: 0.42)))
            }
        }
        .saturation(0)
    }

    private func stripe(_ context: inout GraphicsContext, rect: CGRect, shade: Double) {
        context.fill(Path(rect), with: .color(Color(white: shade)))
    }

    private func diagonal(_ context: inout GraphicsContext, size: CGSize, from: CGPoint, to: CGPoint, width: CGFloat, shade: Double) {
        var path = Path()
        path.move(to: from)
        path.addLine(to: to)
        context.stroke(path, with: .color(Color(white: shade)), lineWidth: width)
    }
}

struct LanguageSongbooksView: View {
    @EnvironmentObject private var library: HymnLibrary
    let languageCode: String
    let title: String

    private var books: [Songbook] {
        library.songbooks.filter { $0.language == languageCode }
    }

    var body: some View {
        List(books) { songbook in
            NavigationLink {
                SongbookDetailView(songbook: songbook)
            } label: {
                VStack(alignment: .leading, spacing: 4) {
                    Text(songbook.title).font(.headline)
                    Text("\(songbook.hymnCount) песен").font(.subheadline).foregroundStyle(.secondary)
                }.padding(.vertical, 4)
            }
        }
        .navigationTitle(title)
        .navigationBarTitleDisplayMode(.large)
    }
}
