import type { Metadata } from 'next';
import { ArrowLeft, Database, Mail, ShieldCheck, Smartphone } from 'lucide-react';
import Image from 'next/image';
import Link from 'next/link';

export const metadata: Metadata = {
  title: 'Политика конфиденциальности — Гимны',
  description: 'Политика конфиденциальности приложения «Гимны» для iOS.',
};

export default function Privacy() {
  return (
    <main className="legal-page">
      <header className="legal-header">
        <Link className="brand" href="/"><Image src="/app-icon.png" width={36} height={36} alt="" /><span>Гимны</span></Link>
        <Link className="back-link" href="/"><ArrowLeft aria-hidden="true" />Вернуться в поддержку</Link>
      </header>

      <article className="legal-document">
        <p className="eyebrow">Действует с 31 августа 2026 года</p>
        <h1>Политика конфиденциальности</h1>
        <p className="legal-lead">Приложение «Гимны» создано с уважением к вашей частной жизни. Оно работает без регистрации и не собирает персональные данные.</p>

        <div className="privacy-summary">
          <div><ShieldCheck aria-hidden="true" /><strong>Без отслеживания</strong><span>Нет рекламы, аналитических трекеров и профилирования.</span></div>
          <div><Database aria-hidden="true" /><strong>Без передачи данных</strong><span>Поисковые запросы и избранное не отправляются разработчику.</span></div>
          <div><Smartphone aria-hidden="true" /><strong>Только на устройстве</strong><span>Настройки, избранное и быстрый доступ сохраняются локально на iPhone или iPad.</span></div>
        </div>

        <section><h2>Какие данные обрабатывает приложение</h2><p>Приложение не собирает, не хранит на внешних серверах и не передаёт третьим лицам личные данные, идентификаторы устройства, местоположение, контакты, фотографии, историю поиска или сведения об использовании.</p></section>
        <section><h2>Локальные данные</h2><p>Выбранный язык интерфейса, размер текста, избранные гимны и закреплённые сборники хранятся в системном локальном хранилище приложения. Эти сведения остаются на устройстве и могут быть удалены вместе с приложением.</p></section>
        <section><h2>Интернет и сторонние сервисы</h2><p>Основные функции приложения работают офлайн. В текущей версии нет сторонних рекламных, аналитических, платёжных или социальных SDK. Если это изменится, политика и декларация App Privacy будут обновлены до выпуска соответствующей версии.</p></section>
        <section><h2>Детская конфиденциальность</h2><p>Приложение не запрашивает возраст и не собирает данные детей или взрослых. Оно не содержит пользовательских аккаунтов, общения между пользователями или персонализированной рекламы.</p></section>
        <section><h2>Изменения политики</h2><p>Дата вступления в силу указана в начале страницы. Существенные изменения будут опубликованы здесь до выпуска версии приложения, которая меняет работу с данными.</p></section>
        <section><h2>Контакты</h2><p>По вопросам конфиденциальности напишите разработчику Александру Телегину:</p><a className="legal-contact" href="mailto:teleginalex2905@gmail.com"><Mail aria-hidden="true" />teleginalex2905@gmail.com</a></section>
      </article>
    </main>
  );
}
