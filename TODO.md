# רשימת משימות להשלמת האתר — עו״ד אודליה אייזנקייט

## 1. הגדרות בסיסיות (config.js)
- [x] שם מלא — אודליה אייזנקייט
- [x] מספר רישיון — 67020
- [x] שנות ניסיון — 12
- [x] השכלה — LL.B
- [x] טלפון — 050-2899933
- [x] כתובת — ארלוזרוב 17, הוד השרון
- [ ] **אימייל** — לעדכן כתובת אימייל אמיתית (כרגע: lawodelia@gmail.com)
- [ ] **רשתות חברתיות** — לעדכן לינקים אמיתיים לפייסבוק, אינסטגרם ולינקדאין
- [ ] **Google Analytics ID** — להוסיף קוד מעקב (כרגע placeholder)
- [ ] **כתובת האתר** — לעדכן URL סופי ב-siteUrl

## 2. תמונות (חובה!)
- [ ] **תמונת פרופיל** (portrait.jpg) — צילום מקצועי של אודליה
      → ראי prompts/02-portrait-photo.txt להנחיות לצלם
      → שמרי ב: images/portrait.jpg (680x880px מומלץ)
- [ ] **תמונת רקע Hero** (hero-bg.jpg) — ייצור עם Gemini
      → ראי prompts/01-hero-background.txt לפרומפט
      → שמרי ב: images/hero-bg.jpg (1920x1080px)
- [ ] **תמונת OG/שיתוף** (og-image.jpg) — ליצור עם Gemini
      → ראי prompts/03-og-image.txt לפרומפט
      → שמרי ב: images/og-image.jpg (1200x630px בדיוק!)
- [ ] **תמונת אודות** (about.jpg) — צילום מקצועי או AI
      → ראי prompts/04-about-section-image.txt
      → שמרי ב: images/about.jpg
- [ ] **תמונות מאמרים** — ליצור עם Gemini (6 תמונות)
      → prompts/05 עד 12 — כל קובץ מכיל פרומפט ספציפי
      → שמרי ב: images/article-family.jpg, article-poa.jpg, article-wills.jpg, article-mediation.jpg, article-contracts.jpg, article-consumer.jpg, article-corporate.jpg, article-risk.jpg

## 3. דומיין ואחסון
- [ ] **רכישת דומיין** — odelia-law.co.il (או דומיין אחר)
- [ ] **אחסון** — בחירת שירות אחסון (Netlify/Vercel/שרת ישראלי)
- [ ] **תעודת SSL** — וידוא HTTPS (בדרך כלל מגיע חינם עם האחסון)
- [ ] **העלאת הקבצים** — כל התיקייה Odelia לשרת

## 4. Google ו-SEO
- [ ] **Google Search Console** — רישום האתר ואימות בעלות
- [ ] **Google Business Profile** — יצירת/עדכון פרופיל עסקי בגוגל
      → כתובת: ארלוזרוב 17, הוד השרון
      → קטגוריה: עורכת דין / משרד עורכי דין
      → שעות פעילות, טלפון, תמונות
- [ ] **Google Maps Embed** — לעדכן ב-config.js את ה-googleMapsEmbed URL
      → להיכנס ל-Google Maps → לחפש את הכתובת → Share → Embed → להעתיק URL
- [ ] **sitemap.xml** — ליצור ולהעלות sitemap (אפשר אוטומטית עם כלי חינמי)
- [ ] **robots.txt** — ליצור קובץ robots.txt בסיסי
- [ ] **Google Analytics** — הקמת חשבון GA4 ועדכון ה-ID ב-config.js

## 5. טופס צור קשר
- [ ] **שירות טפסים** — לחבר את הטופס לשירות שליחת מיילים
      → אפשרויות מומלצות:
        - Formspree (חינם עד 50 הודעות/חודש)
        - EmailJS
        - Netlify Forms (אם מאחסנים ב-Netlify)
      → לעדכן את ה-form action בקוד

## 6. נגישות (חובה חוקית!)
- [ ] **תקן נגישות** — התקנת כפתור נגישות פעיל
      → להטמיע סקריפט נגישות כמו: UserWay, Nagich, או EqualWeb
      → חובה חוקית לפי תקנות שוויון זכויות לאנשים עם מוגבלות (התאמות נגישות לשירות), תשע"ג-2013
- [ ] **הצהרת נגישות** — להוסיף עמוד הצהרת נגישות

## 7. משפטי (חובה!)
- [ ] **מדיניות פרטיות** — ליצור עמוד מדיניות פרטיות
      → חובה לפי חוק הגנת הפרטיות, תשמ"א-1981
      → במיוחד אם יש טופס יצירת קשר / איסוף מידע
- [ ] **תנאי שימוש** — ליצור עמוד תנאי שימוש באתר
- [ ] **הסתייגות** — כבר קיים בפוטר ("אתר זה אינו מהווה ייעוץ משפטי") ✓

## 8. שיפורים מומלצים (לא דחוף)
- [ ] **Favicon** — ליצור favicon מקצועי (כרגע emoji scales)
      → מומלץ: לוגו קטן של המשרד בפורמט .ico ו-.png
- [ ] **לוגו** — עיצוב לוגו מקצועי למשרד
- [ ] **ביקורות Google** — לעודד לקוחות לכתוב ביקורות בגוגל
- [ ] **WhatsApp Business** — הקמת חשבון WhatsApp Business
- [ ] **ניוזלטר** — שקילת הוספת הרשמה לניוזלטר
- [ ] **בלוג פעיל** — הוספת מאמרים חדשים אחת לחודש-חודשיים (מצוין ל-SEO)
- [ ] **מהירות טעינה** — אופטימיזציה של תמונות (WebP format, compression)
- [ ] **Schema.org נוסף** — הוספת FAQ Schema למאמרים

## 9. בדיקות לפני עלייה לאוויר
- [ ] בדיקה בכל הדפדפנים: Chrome, Safari, Firefox, Edge
- [ ] בדיקה במובייל: iPhone, Android
- [ ] בדיקת כל הלינקים עובדים
- [ ] בדיקת טופס צור קשר שולח באמת
- [ ] בדיקת כפתור WhatsApp פותח שיחה נכונה
- [ ] בדיקת מהירות טעינה ב-Google PageSpeed Insights
- [ ] בדיקת SEO ב-Google Lighthouse
- [ ] בדיקת נגישות ב-WAVE accessibility tool

## 10. לאחר עלייה לאוויר
- [ ] שליחת sitemap ל-Google Search Console
- [ ] הוספת האתר ל-Google Business Profile
- [ ] שיתוף ברשתות החברתיות
- [ ] מעקב אחר ביצועים ב-Google Analytics
- [ ] מעקב אחר דירוג חיפוש ב-Google Search Console
