# import feedparser
# import os
# import requests
# from newspaper import Article
# from dotenv import load_dotenv
# from datetime import datetime
# import html as html_lib
# import json

# # Load environment variables
# load_dotenv()

# AZURE_OPENAI_API_KEY = os.getenv("AZURE_OPENAI_API_KEY")
# AZURE_OPENAI_ENDPOINT = os.getenv("AZURE_OPENAI_ENDPOINT")
# AZURE_OPENAI_API_VERSION = os.getenv("AZURE_OPENAI_API_VERSION")
# TO_EMAIL = os.getenv("TO_EMAIL")
# HEADSIN_PASSWORD = "sJYlSh9xKM4K40"


# RSS_FEEDS = [
#     "https://economictimes.indiatimes.com/jobs/fresher/rssfeeds/97860609.cms",
#     "https://economictimes.indiatimes.com/jobs/mid-career/rssfeeds/97860586.cms",
#     "https://economictimes.indiatimes.com/jobs/rssfeeds/107115.cms",
#     "https://hr.economictimes.indiatimes.com/rss/workplace-4-0/employee-engagement"
# ]

# def clean_summary_paragraph(text):
#     import re
#     text = re.sub(r'\s*\n\s*', ' ', text)      # Replace newlines with space
#     text = re.sub(r'\s{2,}', ' ', text).strip()  # Collapse multiple spaces
#     return text



# # === Extract image from article ===
# def extract_image(url):
#     try:
#         article = Article(url)
#         article.download()
#         article.parse()
#         return article.top_image
#     except:
#         return None

# # === Gather all articles from RSS feeds ===
# def gather_all_articles():
#     all_articles = []
    
#     for feed_url in RSS_FEEDS:
#         print(f"📡 Fetching from: {feed_url}")
#         try:
#             feed = feedparser.parse(feed_url)
#             for entry in feed.entries[:10]:  # Get more entries per feed
#                 title = entry.get("title", "").strip()
#                 link = entry.get("link", "")
#                 description = entry.get("description", "") or entry.get("summary", "")
                
#                 # Clean description (remove HTML tags)
#                 if description:
#                     import re
#                     description = re.sub(r'<[^>]+>', '', description).strip()
                
#                 if not title or not link or len(description) < 50:
#                     continue
                
#                 print(f"📄 Gathered: {title[:60]}...")
                
#                 # Get image URL
#                 image_url = extract_image(link)
                
#                 all_articles.append({
#                     "title": title,
#                     "link": link,
#                     "description": description,
#                     "image": image_url,
#                     "feed_source": feed_url
#                 })
        
#         except Exception as e:
#             print(f"❌ Error fetching from {feed_url}: {e}")
#             continue
    
#     print(f"📊 Total articles gathered: {len(all_articles)}")
#     return all_articles

# # === AI Analysis and Ranking ===
# def ai_rank_articles(articles):
#     """Send all articles to AI for ranking and selection of top 5"""
    
#     # Prepare articles data for AI
#     articles_for_ai = []
#     for i, article in enumerate(articles):
#         articles_for_ai.append({
#             "id": i,
#             "title": article["title"],
#             "description": article["description"][:500]  # Limit description length
#         })
    
#     prompt = f"""
# You are an AI assistant curating a newsletter for job seekers and career professionals.

# Analyze these {len(articles_for_ai)} articles and select EXACTLY 5 BEST articles for job seekers.

# Focus on articles about:
# - Interview preparation and tips
# - Resume writing and optimization  
# - Career development and growth
# - Job search strategies
# - Workplace skills and advice
# - Internship guidance
# - Professional networking
# - Skill development

# AVOID: Job listings, company news, general business news, promotional content.

# For each of the TOP 5 articles, write a detailed summary (60-80 words) explaining what specific advice the article provides and why it's valuable.

# IMPORTANT: Respond with ONLY valid JSON array format. No extra text before or after.

# [
#   {{"id": 5, "summary": "This comprehensive guide provides job seekers with proven strategies for answering challenging interview questions. It covers the STAR method for behavioral questions, salary negotiation techniques, and how to address weaknesses professionally. The article includes real examples and actionable scripts that candidates can use to build confidence and improve their interview performance significantly."}},
#   {{"id": 12, "summary": "A detailed walkthrough of resume optimization techniques designed to pass Applicant Tracking Systems while appealing to recruiters. The article explains keyword integration, proper formatting, and customization strategies for different industries. It provides templates and common pitfalls to avoid, helping job seekers improve their resume visibility and response rates."}}
# ]

# Articles:
# {json.dumps(articles_for_ai, indent=1)}
# """

#     try:
#         response = requests.post(
#             AZURE_OPENAI_ENDPOINT,
#             headers={
#                 "Content-Type": "application/json",
#                 "api-key": AZURE_OPENAI_API_KEY,
#             },
#             json={
#                 "messages": [{"role": "user", "content": prompt}],
#                 "temperature": 0.3, 
#                 "max_tokens": 4000,
#                 "top_p": 0.9,
#             },
#             params={"api-version": AZURE_OPENAI_API_VERSION},
#         )
        
#         data = response.json()
#         ai_response = data["choices"][0]["message"]["content"].strip()
        
#         # Clean and parse AI response
#         try:
#             # Extract JSON from response (in case AI adds extra text)
#             import re
#             json_match = re.search(r'\[.*\]', ai_response, re.DOTALL)
#             if json_match:
#                 json_str = json_match.group(0)
#             else:
#                 json_str = ai_response
            
#             ranked_articles = json.loads(json_str)
            
#         except json.JSONDecodeError as e:
#             print(f"❌ JSON parsing failed: {e}")
#             print(f"AI Response: {ai_response[:500]}...")
#             # Fallback: use first 10 articles
#             print("🔄 Using fallback selection...")
#             return articles[:10]
        
#         # Build final articles list with AI rankings
#         final_articles = []
#         for ranked in ranked_articles:
#             try:
#                 article_id = ranked["id"]
#                 if article_id < len(articles):
#                     article = articles[article_id].copy()
#                     article["ai_summary"] = ranked["summary"]
#                     final_articles.append(article)
#             except (KeyError, TypeError) as e:
#                 print(f"❌ Error processing ranked article: {e}")
#                 continue
        
#         # Ensure exactly 10 articles
#         final_articles = final_articles[:5]
        
#         # If we don't have enough articles, pad with original articles
#         if len(final_articles) < 5:
#             remaining_needed = 5 - len(final_articles)
#             used_ids = {articles.index(art) for art in final_articles if art in articles}
#             for i, article in enumerate(articles):
#                 if i not in used_ids and remaining_needed > 0:
#                     final_articles.append(article)
#                     remaining_needed -= 1
        
#         print(f"🤖 AI selected exactly {len(final_articles)} top articles:")
#         for i, article in enumerate(final_articles, 1):
#             print(f"{i}. {article['title'][:60]}...")
        
#         return final_articles
        
#     except Exception as e:
#         print(f"❌ AI ranking error: {e}")
#         # Fallback: return first 10 articles if AI fails
#         return articles[:10]

# # === Generate HTML Newsletter ===
# def generate_html(articles):
#     html = f"""
#     <div style="font-family:Georgia,serif;max-width:700px;margin:auto;padding:0;">
      
#       <!-- Header -->
#       <div
#       style="background-color:#663399;padding:20px;text-align:center;margin-bottom:10px;border-radius:10px 10px 0 0;">
#       <img src="https://www.dropbox.com/scl/fi/q7e1gpaj3bn1hf1300oue/unnamed.png?rlkey=yesdj3i6w9piwmmqr2x7h5w5j&st=9q74ym9q&dl=1
# " alt="Logo" style="height:40px;">
#     </div>

#     <!-- Content -->
#     <div style="padding:0 20px;">
#       <div style="padding: 0 20px; text-align: center;">
#         <h2 style="
#         font-size: clamp(30px, 5vw, 60px);
#         font-family: 'Times New Roman', Times, serif;
#         margin: 0;
#         line-height: 1.3;
#         color: #2e2e2e;
#         text-align: center;
#         ">
#         Weekly Digest
#         </h2>
#       </div>



#       <hr>

#       <h2 style="text-align:center;font-size:18px;margin-bottom:10px;font-family: Poppins, sans-serif;">
#         TODAY'S HIGHLIGHTS
#       </h2>

#       <hr>
#     """
    
#     for i, article in enumerate(articles, 1):
#         html += f"""
#         <div style="border-bottom:1px solid #ddd;margin-bottom:30px;padding-bottom:20px;">
#           <h3 style="margin:0 0 10px;">
#             <a href="{article['link']}" style="color:#2e6da4;text-decoration:none;font-size:20px;">{html_lib.escape(article['title'])}</a>
#           </h3>
#         """
        
#         if article['image']:
#             html += f"""<img src="{article['image']}" alt="image" style="max-width:100%;border-radius:8px;margin:10px 0;">"""

#         # Use AI summary (should be detailed paragraph)
#         summary_text = article.get('ai_summary', article['description'][:300])
#         html += f"""<p style="font-size:17px;color:#444;line-height:1.7;margin:10px 0;">{html_lib.escape(summary_text)}</p>"""

#         html += "</div>"

#     html += f"""
#       </div>
          
#           <!-- Footer -->
#           <div style="background-color:#f5f5f5;padding:30px 20px;text-align:center;margin-top:40px;border-radius:0 0 10px 10px;">

#         <!-- Greeting -->
#         <p style="color:#888;font-size:12px;margin:10px 0;">
#         <strong>
#             <span style="color:#888;font-family: Poppins, sans-serif;">THANK YOU FOR CHOOSING HEADSIN.</span>
#         </strong>
#         </p>

#         <br>

#         <!-- Social Icons -->
#         <div style="margin-bottom: 15px;">
#             <!-- Facebook -->
#             <a href="https://www.facebook.com/people/HeadsInco/61574907748702/" style="margin: 0 10px; text-decoration: none;">
#             <img src="https://img.icons8.com/ios-filled/50/ffffff/facebook-new.png" alt="Facebook"
#                 style="background-color: #df6789; padding: 8px; border-radius: 50%; width: 32px; height: 32px;" />
#             </a>

#             <!-- LinkedIn -->
#             <a href="https://www.linkedin.com/company/headsinco" style="margin: 0 10px; text-decoration: none;">
#             <img src="https://img.icons8.com/ios-filled/50/ffffff/linkedin.png" alt="LinkedIn"
#                 style="background-color: #df6789; padding: 8px; border-radius: 50%; width: 32px; height: 32px;" />
#             </a>

#             <!-- Twitter/X -->
#             <a href="https://x.com/HeadsIn_co" style="margin: 0 10px; text-decoration: none;">
#             <img src="https://img.icons8.com/ios-filled/50/ffffff/twitterx.png" alt="TwitterX"
#                 style="background-color: #df6789; padding: 8px; border-radius: 50%; width: 32px; height: 32px;" />
#             </a>

#             <!-- Instagram -->
#             <a href="https://www.instagram.com/headsin.co" style="margin: 0 10px; text-decoration: none;">
#             <img src="https://img.icons8.com/ios-filled/50/ffffff/instagram-new.png" alt="Instagram"
#                 style="background-color: #df6789; padding: 8px; border-radius: 50%; width: 32px; height: 32px;" />
#             </a>
#         </div>

#         <!-- Copyright -->
#         <p style="color:#888;font-size:14px;margin:10px 0;">© 2025 Headsin. All rights reserved.</p>

#         <!-- Address -->
#         <p style="color:#888;font-size:12px;margin:10px 0;">
#             SY-404 | Surat, Gujarat, India - 395004
#         </p>

#         <!-- Preferences -->
#         <p style="color:#888;font-size:12px;margin:15px 0;">
#             Customize your job alerts? <a href="https://headsin.co/dashboard/profile" style="color:#663399;text-decoration:none;">Update Settings</a>
#             or <a href="{{{{unsubscribeUrl}}}}" style="color:#663399;text-decoration:none;">Unsubscribe</a>
#         </p>

#         </div>

          
#         </div>
#     """
#     return html

# # === Send newsletter ===
# def send_newsletter_via_heads_in(html_template):
#     HEADSIN_API_URL = "https://application-api.headsin.co/api/v1/newsletter-broadcasts"
#     headers = {
#         "Content-Type": "application/json"
#     }
#     payload = {
#         "template": html_template,
#         "password": HEADSIN_PASSWORD,
#         "sendTo": [],
#         "placeholders": ["{{unsubscribeUrl}}"]
#     }

#     try:
#         response = requests.post(HEADSIN_API_URL, headers=headers, json=payload)
#         if response.status_code == 200:
#             print("✅ Newsletter sent successfully to all users!")
#         else:
#             print(f"❌ Failed to send newsletter. Status: {response.status_code}")
#             print("Response:", response.text)
#     except Exception as e:
#         print("❌ Exception during sending:", str(e))



# # === Main ===
# if __name__ == "__main__":
#     print("🚀 Starting AI-powered newsletter generation...")
    
#     # Step 1: Gather all articles with title, description, image
#     all_articles = gather_all_articles()
    
#     if not all_articles:
#         print("⚠️ No articles found from RSS feeds.")
#         exit()
    
#     # Step 2: AI analysis and ranking (title + description only)
#     top_articles = ai_rank_articles(all_articles)
    
#     if not top_articles:
#         print("⚠️ AI could not select any relevant articles.")
#         exit()
    
#     # Step 3: Generate and send newsletter
#     print(f"📧 Generating newsletter with {len(top_articles)} AI-selected articles...")
#     html = generate_html(top_articles)
#     print(html)
#     send_newsletter_via_heads_in(html)
