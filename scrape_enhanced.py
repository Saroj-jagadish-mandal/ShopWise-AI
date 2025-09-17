# import time
# import json
# from selenium import webdriver
# from selenium.webdriver.chrome.service import Service
# from selenium.webdriver.chrome.options import Options
# from selenium.webdriver.common.by import By
# from selenium.webdriver.support.ui import WebDriverWait
# from selenium.webdriver.support import expected_conditions as EC
# from selenium.common.exceptions import TimeoutException, NoSuchElementException
# import re

# class AmazonProductScraper:
#     def __init__(self, chrome_driver_path):
#         self.chrome_driver_path = chrome_driver_path
#         self.driver = None
        
#     def setup_driver(self):
#         """Setup Chrome driver with optimized options"""
#         print("Launching Chrome browser...")
        
#         options = Options()
#         # Add user agent to avoid detection
#         options.add_argument("--user-agent=Mozilla/5.0 (Windows NT 10.0; Win64; x64) AppleWebKit/537.36 (KHTML, like Gecko) Chrome/91.0.4472.124 Safari/537.36")
#         # Disable images for faster loading
#         options.add_argument("--disable-images")
#         # Disable notifications
#         options.add_argument("--disable-notifications")
#         # Add other useful options
#         options.add_argument("--no-sandbox")
#         options.add_argument("--disable-dev-shm-usage")
#         options.add_argument("--disable-blink-features=AutomationControlled")
#         options.add_experimental_option("excludeSwitches", ["enable-automation"])
#         options.add_experimental_option('useAutomationExtension', False)
#         # Run headless for Streamlit (optional - remove if you want to see browser)
#         # options.add_argument("--headless")
        
#         service = Service(self.chrome_driver_path)
#         self.driver = webdriver.Chrome(service=service, options=options)
        
#         # Execute script to prevent detection
#         self.driver.execute_script("Object.defineProperty(navigator, 'webdriver', {get: () => undefined})")
        
#     def safe_find_element(self, by, value, timeout=10):
#         """Safely find element with timeout"""
#         try:
#             element = WebDriverWait(self.driver, timeout).until(
#                 EC.presence_of_element_located((by, value))
#             )
#             return element
#         except TimeoutException:
#             return None
            
#     def safe_find_elements(self, by, value):
#         """Safely find multiple elements"""
#         try:
#             return self.driver.find_elements(by, value)
#         except NoSuchElementException:
#             return []
            
#     def extract_text_safe(self, element):
#         """Safely extract text from element"""
#         try:
#             return element.text.strip() if element else None
#         except:
#             return None
            
#     def extract_attribute_safe(self, element, attribute):
#         """Safely extract attribute from element"""
#         try:
#             return element.get_attribute(attribute) if element else None
#         except:
#             return None

#     def scrape_product_data(self, product_url):
#         """Scrape comprehensive product data from Amazon"""
#         try:
#             self.setup_driver()
#             self.driver.get(product_url)
#             print("Page loaded...")
            
#             # Wait for page to load
#             time.sleep(3)
            
#             product_data = {}
            
#             # 1. Product Title
#             title_selectors = [
#                 "#productTitle",
#                 "h1.a-size-large.a-spacing-none",
#                 "[data-automation-id='product-title']",
#                 "h1[class*='product-title']"
#             ]
#             for selector in title_selectors:
#                 title_element = self.safe_find_element(By.CSS_SELECTOR, selector)
#                 if title_element:
#                     product_data['title'] = self.extract_text_safe(title_element)
#                     break
            
#             # 2. Price Information
#             price_selectors = [
#                 ".a-price-whole",
#                 ".a-price .a-offscreen",
#                 "[data-automation-id='product-price']",
#                 ".a-price-symbol + .a-price-whole",
#                 "span.a-price.a-text-price.a-size-medium.apexPriceToPay"
#             ]
#             for selector in price_selectors:
#                 price_element = self.safe_find_element(By.CSS_SELECTOR, selector)
#                 if price_element:
#                     price_text = self.extract_text_safe(price_element)
#                     if price_text:
#                         product_data['current_price'] = price_text
#                         break
                        
#             # Original/List Price
#             original_price_selectors = [
#                 ".a-text-price .a-offscreen",
#                 "[data-automation-id='list-price']",
#                 "span.a-price.a-text-price"
#             ]
#             for selector in original_price_selectors:
#                 orig_price_element = self.safe_find_element(By.CSS_SELECTOR, selector)
#                 if orig_price_element:
#                     orig_price_text = self.extract_text_safe(orig_price_element)
#                     if orig_price_text and orig_price_text != product_data.get('current_price'):
#                         product_data['original_price'] = orig_price_text
#                         break
            
#             # 3. Product Images
#             image_selectors = [
#                 "#altImages img",
#                 "#landingImage",
#                 "[data-automation-id='product-image']",
#                 "img[data-a-image-name]"
#             ]
#             images = []
#             for selector in image_selectors:
#                 image_elements = self.safe_find_elements(By.CSS_SELECTOR, selector)
#                 for img in image_elements[:10]:  # Limit to 10 images
#                     src = self.extract_attribute_safe(img, 'src')
#                     data_src = self.extract_attribute_safe(img, 'data-src')
#                     img_url = src or data_src
#                     if img_url and 'https' in img_url and img_url not in images:
#                         images.append(img_url)
#             product_data['images'] = images
            
#             # 4. Product Rating
#             rating_selectors = [
#                 "span.a-icon-alt",
#                 "[data-automation-id='product-rating'] span",
#                 ".a-icon.a-icon-star span",
#                 "i[class*='a-icon-star'] span"
#             ]
#             for selector in rating_selectors:
#                 rating_element = self.safe_find_element(By.CSS_SELECTOR, selector)
#                 if rating_element:
#                     rating_text = self.extract_text_safe(rating_element)
#                     if rating_text and ('out of' in rating_text or 'stars' in rating_text):
#                         product_data['rating'] = rating_text
#                         break
            
#             # 5. Number of Reviews
#             review_count_selectors = [
#                 "#acrCustomerReviewText",
#                 "[data-automation-id='reviews-count']",
#                 "a[href*='#reviews'] span",
#                 "span[id*='acrCustomerReviewText']"
#             ]
#             for selector in review_count_selectors:
#                 review_element = self.safe_find_element(By.CSS_SELECTOR, selector)
#                 if review_element:
#                     review_text = self.extract_text_safe(review_element)
#                     if review_text:
#                         product_data['review_count'] = review_text
#                         break
            
#             # 6. Product Description/Features
#             description_selectors = [
#                 "#feature-bullets ul",
#                 "#productDescription",
#                 "[data-automation-id='product-overview']",
#                 "#featurebullets_feature_div ul"
#             ]
#             for selector in description_selectors:
#                 desc_element = self.safe_find_element(By.CSS_SELECTOR, selector)
#                 if desc_element:
#                     desc_text = self.extract_text_safe(desc_element)
#                     if desc_text and len(desc_text) > 50:  # Ensure meaningful description
#                         product_data['description'] = desc_text
#                         break
            
#             # 7. Product Specifications
#             spec_selectors = [
#                 "#productDetails_techSpec_section_1 tr",
#                 "#productDetails_detailBullets_sections1 tr",
#                 "#productDetails_feature_div tr"
#             ]
#             specifications = {}
#             for selector in spec_selectors:
#                 spec_elements = self.safe_find_elements(By.CSS_SELECTOR, selector)
#                 for spec in spec_elements:
#                     try:
#                         key_elem = spec.find_element(By.CSS_SELECTOR, "td:first-child, th")
#                         value_elem = spec.find_element(By.CSS_SELECTOR, "td:last-child")
#                         key = self.extract_text_safe(key_elem)
#                         value = self.extract_text_safe(value_elem)
#                         if key and value and key != value:
#                             specifications[key] = value
#                     except:
#                         continue
#             product_data['specifications'] = specifications
            
#             # 8. Brand Information
#             brand_selectors = [
#                 "#bylineInfo",
#                 "[data-automation-id='product-brand']",
#                 "a[id*='brand']",
#                 "span.a-size-base"
#             ]
#             for selector in brand_selectors:
#                 brand_element = self.safe_find_element(By.CSS_SELECTOR, selector)
#                 if brand_element:
#                     brand_text = self.extract_text_safe(brand_element)
#                     if brand_text and 'visit' not in brand_text.lower():
#                         product_data['brand'] = brand_text
#                         break
            
#             # 9. Availability Status
#             availability_selectors = [
#                 "#availability span",
#                 "[data-automation-id='availability-message']",
#                 "#availability .a-color-state",
#                 "#availability .a-color-success"
#             ]
#             for selector in availability_selectors:
#                 avail_element = self.safe_find_element(By.CSS_SELECTOR, selector)
#                 if avail_element:
#                     avail_text = self.extract_text_safe(avail_element)
#                     if avail_text:
#                         product_data['availability'] = avail_text
#                         break
            
#             # 10. Product Variants (Color, Size, etc.)
#             variant_selectors = [
#                 "#variation_color_name li",
#                 "#variation_size_name li",
#                 "[data-automation-id='product-variants'] li"
#             ]
#             variants = []
#             for selector in variant_selectors:
#                 variant_elements = self.safe_find_elements(By.CSS_SELECTOR, selector)
#                 for variant in variant_elements:
#                     variant_text = self.extract_text_safe(variant)
#                     if variant_text:
#                         variants.append(variant_text)
#             product_data['variants'] = variants
            
#             # 11. Customer Questions & Answers (first few)
#             qa_selectors = [
#                 "[data-automation-id='qa-block'] div",
#                 "#ask-btf_feature_div .a-section"
#             ]
#             qa_data = []
#             for selector in qa_selectors:
#                 qa_elements = self.safe_find_elements(By.CSS_SELECTOR, selector)
#                 for qa in qa_elements[:5]:  # Limit to first 5 Q&As
#                     qa_text = self.extract_text_safe(qa)
#                     if qa_text and len(qa_text) > 20:
#                         qa_data.append(qa_text)
#             product_data['qa'] = qa_data
            
#             # 12. Related/Recommended Products
#             related_selectors = [
#                 "[data-automation-id='related-products'] a",
#                 "#similarities a",
#                 ".a-carousel-card a"
#             ]
#             related_products = []
#             for selector in related_selectors:
#                 related_elements = self.safe_find_elements(By.CSS_SELECTOR, selector)
#                 for related in related_elements[:10]:  # Limit to 10
#                     title = self.extract_attribute_safe(related, 'title')
#                     href = self.extract_attribute_safe(related, 'href')
#                     if title and href:
#                         if not href.startswith('http'):
#                             href = 'https://amazon.com' + href
#                         related_products.append({'title': title, 'url': href})
#             product_data['related_products'] = related_products
            
#             # 13. Categories/Breadcrumb
#             breadcrumb_selectors = [
#                 "#wayfinding-breadcrumbs_feature_div a",
#                 "#nav-subnav a",
#                 ".a-breadcrumb a"
#             ]
#             categories = []
#             for selector in breadcrumb_selectors:
#                 breadcrumb_elements = self.safe_find_elements(By.CSS_SELECTOR, selector)
#                 for breadcrumb in breadcrumb_elements:
#                     category = self.extract_text_safe(breadcrumb)
#                     if category and category not in categories:
#                         categories.append(category)
#             product_data['categories'] = categories
            
#             # 14. Prime/Shipping Information
#             shipping_selectors = [
#                 "[data-automation-id='shipping-info']",
#                 "#mir-layout-DELIVERY_BLOCK span",
#                 "#primelogo_feature_div",
#                 ".a-color-success"
#             ]
#             shipping_info = []
#             for selector in shipping_selectors:
#                 shipping_elements = self.safe_find_elements(By.CSS_SELECTOR, selector)
#                 for shipping in shipping_elements:
#                     shipping_text = self.extract_text_safe(shipping)
#                     if shipping_text and len(shipping_text) > 5:
#                         shipping_info.append(shipping_text)
#             product_data['shipping_info'] = shipping_info
            
#             # 15. Best Seller Rank
#             rank_selectors = [
#                 "#SalesRank",
#                 "[data-automation-id='sales-rank']",
#                 "#detailBulletsWrapper_feature_div"
#             ]
#             for selector in rank_selectors:
#                 rank_element = self.safe_find_element(By.CSS_SELECTOR, selector)
#                 if rank_element:
#                     rank_text = self.extract_text_safe(rank_element)
#                     if rank_text and 'rank' in rank_text.lower():
#                         product_data['sales_rank'] = rank_text
#                         break
            
#             print("Data extraction completed successfully!")
#             return product_data
            
#         except Exception as e:
#             print(f"Error occurred while scraping: {str(e)}")
#             return None
#         finally:
#             if self.driver:
#                 self.driver.quit()

#     def save_data_to_json(self, data, filename="product_data.json"):
#         """Save scraped data to JSON file"""
#         try:
#             with open(filename, 'w', encoding='utf-8') as f:
#                 json.dump(data, f, ensure_ascii=False, indent=4)
#             print(f"Data saved to {filename}")
#         except Exception as e:
#             print(f"Error saving data: {str(e)}")



# import time
# import json
# from selenium import webdriver
# from selenium.webdriver.chrome.service import Service
# from selenium.webdriver.chrome.options import Options
# from selenium.webdriver.common.by import By
# from selenium.webdriver.support.ui import WebDriverWait
# from selenium.webdriver.support import expected_conditions as EC
# from selenium.common.exceptions import TimeoutException, NoSuchElementException, ElementClickInterceptedException
# import re

# class AmazonProductScraper:
#     def __init__(self, chrome_driver_path):
#         self.chrome_driver_path = chrome_driver_path
#         self.driver = None
        
#     def setup_driver(self):
#         """Setup Chrome driver with optimized options"""
#         print("Launching Chrome browser...")
#         options = Options()
#         options.add_argument("--user-agent=Mozilla/5.0 (Windows NT 10.0; Win64; x64) AppleWebKit/537.36 (KHTML, like Gecko) Chrome/90.0.4430.212 Safari/537.36")
#         options.add_argument("--disable-notifications")
#         options.add_argument("--no-sandbox")
#         options.add_argument("--disable-dev-shm-usage")
#         options.add_argument("--disable-blink-features=AutomationControlled")
#         options.add_experimental_option("excludeSwitches", ["enable-automation"])
#         options.add_experimental_option('useAutomationExtension', False)
#         # Uncomment for headless mode if needed
#         # options.add_argument("--headless=new")
        
#         service = Service(self.chrome_driver_path)
#         self.driver = webdriver.Chrome(service=service, options=options)
#         self.driver.execute_script("Object.defineProperty(navigator, 'webdriver', {get: () => undefined})")
        
#     def safe_find_element(self, by, value, timeout=5):
#         """Safely find element with timeout"""
#         try:
#             element = WebDriverWait(self.driver, timeout).until(
#                 EC.presence_of_element_located((by, value))
#             )
#             return element
#         except TimeoutException:
#             return None
            
#     def safe_find_elements(self, by, value):
#         """Safely find multiple elements"""
#         try:
#             return self.driver.find_elements(by, value)
#         except NoSuchElementException:
#             return []
            
#     def extract_text_safe(self, element):
#         """Safely extract text from element"""
#         try:
#             return element.text.strip() if element else ""
#         except:
#             return ""
            
#     def extract_attribute_safe(self, element, attribute):
#         """Safely extract attribute from element"""
#         try:
#             return element.get_attribute(attribute) if element else ""
#         except:
#             return ""

#     def scrape_product_data(self, product_url):
#         """Scrape comprehensive product data from Amazon using Selenium with provided IDs and all customer reviews"""
#         try:
#             self.setup_driver()
#             self.driver.get(product_url)
#             print("Page loaded...")
            
#             # Wait for critical element (product title)
#             WebDriverWait(self.driver, 10).until(
#                 EC.presence_of_element_located((By.ID, "productTitle"))
#             )
            
#             # Load all reviews by handling pagination
#             try:
#                 WebDriverWait(self.driver, 10).until(
#                     EC.presence_of_element_located((By.ID, "customerReviews"))
#                 )
#                 print("Scrolling to load initial reviews...")
#                 self.driver.execute_script("window.scrollTo(0, document.body.scrollHeight);")
#                 time.sleep(3)  # Increased pause for AJAX-loaded reviews
                
#                 # Click 'See more reviews' if present
#                 see_more = self.safe_find_element(By.CSS_SELECTOR, "a[data-hook='see-all-reviews-link']")
#                 if see_more:
#                     try:
#                         see_more.click()
#                         time.sleep(2)
#                         print("Clicked 'See more reviews'")
#                     except ElementClickInterceptedException:
#                         print("Could not click 'See more reviews' due to interception")
#                     except:
#                         print("Could not click 'See more reviews'")
#             except TimeoutException:
#                 print("Reviews section not found or took too long to load.")
            
#             product_data = {}
            
#             # 1. Product Title
#             title_element = self.safe_find_element(By.ID, "productTitle")
#             product_data['title'] = self.extract_text_safe(title_element)
            
#             # 2. Price Information
#             price_element = self.safe_find_element(By.CSS_SELECTOR, ".a-price .a-offscreen")
#             product_data['current_price'] = self.extract_text_safe(price_element)
            
#             orig_price_element = self.safe_find_element(By.CSS_SELECTOR, ".a-text-price .a-offscreen")
#             product_data['original_price'] = self.extract_text_safe(orig_price_element)
            
#             # 3. Product Features (from feature-bullets)
#             feature_element = self.safe_find_element(By.ID, "feature-bullets")
#             feature_text = self.extract_text_safe(feature_element)
#             product_data['features'] = feature_text if feature_text else ""
            
#             # 4. Product Specifications (from productDetails_techSpec_section_1, productDetails_detailBullets_sections1, prodDetails)
#             specifications = {}
#             spec_selectors = [
#                 "#productDetails_techSpec_section_1 tr",
#                 "#productDetails_detailBullets_sections1 tr",
#                 "#prodDetails tr"
#             ]
#             for selector in spec_selectors:
#                 spec_elements = self.safe_find_elements(By.CSS_SELECTOR, selector)
#                 for spec in spec_elements:
#                     try:
#                         key_elem = spec.find_element(By.CSS_SELECTOR, "td:first-child, th")
#                         value_elem = spec.find_element(By.CSS_SELECTOR, "td:last-child")
#                         key = self.extract_text_safe(key_elem)
#                         value = self.extract_text_safe(value_elem)
#                         if key and value and key != value:
#                             specifications[key] = value
#                     except:
#                         continue
            
#             # Enhance specifications with RAM-specific fields
#             ram_specific_fields = {
#                 "Memory Type": ["Memory Type", "RAM Type", "Module Type", "Technology"],
#                 "Form Factor": ["Form Factor", "Module Format", "DIMM Type"],
#                 "Voltage": ["Voltage", "Operating Voltage"],
#                 "CAS Latency": ["CAS Latency", "Latency", "CL"],
#                 "Pin Count": ["Pin Count", "Pins", "Pin Configuration"],
#                 "ECC": ["ECC", "Error Correction", "Error Checking"],
#                 "Compatibility": ["Compatible Devices", "System Compatibility", "Supported Systems", "Compatibility"]
#             }
            
#             for field, possible_keys in ram_specific_fields.items():
#                 for key in possible_keys:
#                     for spec_key, spec_value in specifications.items():
#                         if key.lower() in spec_key.lower():
#                             specifications[field] = spec_value
#                             break
            
#             # Extract additional details from prodDetails section
#             details_section = self.safe_find_element(By.ID, "prodDetails")
#             if details_section:
#                 details_text = self.extract_text_safe(details_section)
#                 # Extract voltage (e.g., 1.35V, 1.5V)
#                 voltage_match = re.search(r'\b(1\.[35][0-9]*V)\b', details_text)
#                 if voltage_match and "Voltage" not in specifications:
#                     specifications["Voltage"] = voltage_match.group(1)
                
#                 # Extract form factor (e.g., SO-DIMM, DIMM)
#                 form_factor_match = re.search(r'\b(SO-DIMM|DIMM|UDIMM)\b', details_text, re.IGNORECASE)
#                 if form_factor_match and "Form Factor" not in specifications:
#                     specifications["Form Factor"] = form_factor_match.group(1)
                
#                 # Extract pin count (e.g., 204-pin, 240-pin)
#                 pin_match = re.search(r'\b(\d{3}-pin)\b', details_text, re.IGNORECASE)
#                 if pin_match and "Pin Count" not in specifications:
#                     specifications["Pin Count"] = pin_match.group(1)
                
#                 # Extract ECC (e.g., ECC, Non-ECC)
#                 ecc_match = re.search(r'\b(ECC|Non-ECC)\b', details_text, re.IGNORECASE)
#                 if ecc_match and "ECC" not in specifications:
#                     specifications["ECC"] = ecc_match.group(1)
                
#                 # Extract compatibility notes
#                 compat_match = re.search(r'(?:compatible with|supports|works with)\s*([^\.\n]+)', details_text, re.IGNORECASE)
#                 if compat_match and "Compatibility" not in specifications:
#                     specifications["Compatibility"] = compat_match.group(1).strip()
            
#             product_data['specifications'] = specifications
            
#             # 5. Customer Reviews (Extract All Reviews with Pagination)
#             reviews = []
#             review_selectors = [
#                 "#customerReviews .a-section.review",
#                 "#cm-cr-dp-review-list .review",
#                 ".cr-widget-YourReviews .review"
#             ]
#             page_count = 1
#             max_pages = 10  # Safety limit to prevent infinite loops
            
#             while page_count <= max_pages:
#                 print(f"Scraping reviews from page {page_count}...")
#                 review_elements = []
#                 for selector in review_selectors:
#                     review_elements = self.safe_find_elements(By.CSS_SELECTOR, selector)
#                     print(f"Found {len(review_elements)} reviews with selector: {selector} on page {page_count}")
#                     if review_elements:
#                         break
                
#                 for review in review_elements:
#                     try:
#                         review_data = {}
#                         # Review Title
#                         title_elem = review.find_element(By.CSS_SELECTOR, ".review-title")
#                         review_data['title'] = self.extract_text_safe(title_elem)
#                         # Review Text
#                         text_elem = review.find_element(By.CSS_SELECTOR, ".a-expander-content.reviewText.review-text-content.a-expander-partial-collapse-content")
#                         review_data['text'] = self.extract_text_safe(text_elem)
#                         # Review Rating
#                         rating_elem = review.find_element(By.CSS_SELECTOR, ".review-rating")
#                         review_data['rating'] = self.extract_text_safe(rating_elem)
#                         # Customer Name
#                         name_elem = review.find_element(By.CSS_SELECTOR, "span.a-profile-name")
#                         review_data['customer_name'] = self.extract_text_safe(name_elem)
#                         # Helpful Votes
#                         helpful_elem = review.find_element(By.CSS_SELECTOR, ".a-size-small.a-color-secondary")
#                         review_data['helpful_votes'] = self.extract_text_safe(helpful_elem) or "0 people found this helpful"
#                         # Include all reviews with text
#                         if review_data['text']:
#                             reviews.append(review_data)
#                     except Exception as e:
#                         print(f"Error processing review on page {page_count}: {str(e)}")
#                         continue
                
#                 # Check for 'Next page' button
#                 next_page = self.safe_find_element(By.CSS_SELECTOR, "a[title='Next page'], li.a-last a")
#                 if not next_page:
#                     print(f"No more review pages found after page {page_count}")
#                     break
                
#                 try:
#                     next_page.click()
#                     time.sleep(3)  # Wait for next page to load
#                     page_count += 1
#                 except ElementClickInterceptedException:
#                     print(f"Could not click 'Next page' on page {page_count} due to interception")
#                     break
#                 except:
#                     print(f"Could not click 'Next page' on page {page_count}")
#                     break
            
#             product_data['reviews'] = reviews
#             print(f"Collected {len(reviews)} reviews across {page_count} pages")
            
#             # 6. Brand Information
#             brand_element = self.safe_find_element(By.ID, "bylineInfo")
#             product_data['brand'] = self.extract_text_safe(brand_element)
            
#             # 7. Availability Status
#             avail_element = self.safe_find_element(By.ID, "availability")
#             product_data['availability'] = self.extract_text_safe(avail_element)
            
#             # 8. Product Variants
#             variants = []
#             variant_elements = self.safe_find_elements(By.CSS_SELECTOR, "#variation_size_name li, #variation_color_name li")
#             for variant in variant_elements:
#                 variant_text = self.extract_text_safe(variant)
#                 if variant_text:
#                     variants.append(variant_text)
#             product_data['variants'] = variants
            
#             # 9. Customer Questions & Answers
#             qa_data = []
#             qa_elements = self.safe_find_elements(By.CSS_SELECTOR, "#ask-btf_feature_div .a-section")
#             for qa in qa_elements[:10]:
#                 qa_text = self.extract_text_safe(qa)
#                 if qa_text and any(keyword in qa_text.lower() for keyword in ["compatible", "laptop", "ram", "asus"]):
#                     qa_data.append(qa_text)
#             product_data['qa'] = qa_data
            
#             # 10. Related Products
#             related_products = []
#             related_elements = self.safe_find_elements(By.CSS_SELECTOR, "[data-automation-id='related-products'] a, #similarities a")
#             for related in related_elements[:10]:
#                 title = self.extract_attribute_safe(related, 'title')
#                 href = self.extract_attribute_safe(related, 'href')
#                 if title and href:
#                     if not href.startswith('http'):
#                         href = 'https://amazon.com' + href
#                     related_products.append({'title': title, 'url': href})
#             product_data['related_products'] = related_products
            
#             # 11. Categories
#             categories = []
#             breadcrumb_elements = self.safe_find_elements(By.ID, "wayfinding-breadcrumbs_feature_div")
#             for breadcrumb in breadcrumb_elements:
#                 category = self.extract_text_safe(breadcrumb)
#                 if category and category not in categories:
#                     categories.append(category)
#             product_data['categories'] = categories
            
#             # 12. Shipping Information
#             shipping_info = []
#             shipping_elements = self.safe_find_elements(By.ID, "mir-layout-DELIVERY_BLOCK")
#             for shipping in shipping_elements:
#                 shipping_text = self.extract_text_safe(shipping)
#                 if shipping_text and len(shipping_text) > 5:
#                     shipping_info.append(shipping_text)
#             product_data['shipping_info'] = shipping_info
            
#             # 13. Best Seller Rank
#             rank_element = self.safe_find_element(By.ID, "SalesRank")
#             product_data['sales_rank'] = self.extract_text_safe(rank_element)
            
#             # 14. Concatenate text for RAG
#             scraped_text = f"{product_data['title']}\n{product_data['features']}\n"
#             for key, value in product_data['specifications'].items():
#                 scraped_text += f"{key}: {value}\n"
#             for review in product_data['reviews']:
#                 scraped_text += f"Review by {review['customer_name']}: {review['title']} - {review['text']} (Rating: {review['rating']}, Helpful: {review['helpful_votes']})\n"
#             for qa in product_data['qa']:
#                 scraped_text += f"Q&A: {qa}\n"
#             product_data['scraped_text'] = scraped_text
            
#             print("Data extraction completed successfully!")
#             return product_data
            
#         except Exception as e:
#             print(f"Error occurred while scraping: {str(e)}")
#             return None
#         finally:
#             if self.driver:
#                 self.driver.quit()

#     def save_data_to_json(self, data, filename="product_data.json"):
#         """Save scraped data to JSON file"""
#         try:
#             with open(filename, 'w', encoding='utf-8') as f:
#                 json.dump(data, f, ensure_ascii=False, indent=4)
#             print(f"Data saved to {filename}")
#         except Exception as e:
#             print(f"Error saving data: {str(e)}")



import json
from selenium import webdriver
from selenium.webdriver.chrome.service import Service
from selenium.webdriver.chrome.options import Options
from selenium.webdriver.common.by import By
from selenium.webdriver.support.ui import WebDriverWait
from selenium.webdriver.support import expected_conditions as EC
from selenium.common.exceptions import TimeoutException, NoSuchElementException, ElementClickInterceptedException

class AmazonProductScraper:
    def __init__(self, chrome_driver_path):
        self.chrome_driver_path = chrome_driver_path
        self.driver = None
        
    def setup_driver(self):
        """Setup Chrome driver with optimized options"""
        print("Launching Chrome browser...")
        options = Options()
        options.add_argument("--user-agent=Mozilla/5.0 (Windows NT 10.0; Win64; x64) AppleWebKit/537.36 (KHTML, like Gecko) Chrome/120.0.0.0 Safari/537.36")
        options.add_argument("--disable-notifications")
        options.add_argument("--no-sandbox")
        options.add_argument("--disable-dev-shm-usage")
        options.add_argument("--disable-blink-features=AutomationControlled")
        options.add_experimental_option("excludeSwitches", ["enable-automation"])
        options.add_experimental_option('useAutomationExtension', False)
        # Uncomment for headless mode if needed
        # options.add_argument("--headless=new")
        
        service = Service(self.chrome_driver_path)
        self.driver = webdriver.Chrome(service=service, options=options)
        self.driver.execute_script("Object.defineProperty(navigator, 'webdriver', {get: () => undefined})")
        
    def safe_find_element(self, by, value, timeout=3):
        """Find element with reduced timeout"""
        try:
            return WebDriverWait(self.driver, timeout).until(EC.presence_of_element_located((by, value)))
        except TimeoutException:
            return None
            
    def safe_find_elements(self, by, value):
        """Find multiple elements"""
        try:
            return self.driver.find_elements(by, value)
        except NoSuchElementException:
            return []
            
    def extract_text_safe(self, element):
        """Extract text from element"""
        return element.text.strip() if element else ""
            
    def extract_attribute_safe(self, element, attribute):
        """Extract attribute from element"""
        return element.get_attribute(attribute) if element else ""

    def scrape_product_data(self, product_url):
        """Scrape product data from Amazon using Selenium, optimized for all products"""
        try:
            self.setup_driver()
            self.driver.get(product_url)
            print("Page loaded...")
            
            # Wait for critical element (product title)
            WebDriverWait(self.driver, 8).until(EC.presence_of_element_located((By.ID, "productTitle")))
            
            product_data = {}
            
            # 1. Product Title
            product_data['title'] = self.extract_text_safe(self.safe_find_element(By.ID, "productTitle"))
            
            # 2. Price Information
            product_data['current_price'] = self.extract_text_safe(self.safe_find_element(By.CSS_SELECTOR, ".a-price .a-offscreen"))
            product_data['original_price'] = self.extract_text_safe(self.safe_find_element(By.CSS_SELECTOR, ".a-text-price .a-offscreen"))
            
            # 3. Product Features
            product_data['features'] = self.extract_text_safe(self.safe_find_element(By.ID, "feature-bullets"))
            
            # 4. Product Specifications
            specifications = {}
            spec_selectors = [
                "#productDetails_techSpec_section_1 tr",
                "#productDetails_detailBullets_sections1 tr",
                "#prodDetails tr",
                ".prodDetTable tr"
            ]
            for selector in spec_selectors:
                for spec in self.safe_find_elements(By.CSS_SELECTOR, selector):
                    try:
                        key = self.extract_text_safe(spec.find_element(By.CSS_SELECTOR, "td:first-child, th"))
                        value = self.extract_text_safe(spec.find_element(By.CSS_SELECTOR, "td:last-child"))
                        if key and value and key != value:
                            specifications[key] = value
                    except:
                        continue
            product_data['specifications'] = specifications
            
            # 5. Customer Reviews (Extract All with Pagination)
            reviews = []
            review_selector = ".a-section.review, #cm-cr-dp-review-list .review"
            page_count = 1
            max_pages = 5  # Reduced for speed, adjustable
            
            # Check for reviews section
            if self.safe_find_element(By.ID, "customerReviews"):
                print("Scrolling to load reviews...")
                self.driver.execute_script("window.scrollTo(0, document.body.scrollHeight);")
                WebDriverWait(self.driver, 3).until(EC.presence_of_element_located((By.CSS_SELECTOR, review_selector)))
                
                # Click 'See more reviews' if present
                see_more = self.safe_find_element(By.CSS_SELECTOR, "a[data-hook='see-all-reviews-link']")
                if see_more:
                    try:
                        see_more.click()
                        WebDriverWait(self.driver, 3).until(EC.presence_of_element_located((By.CSS_SELECTOR, review_selector)))
                        print("Clicked 'See more reviews'")
                    except:
                        print("Could not click 'See more reviews'")
            
                while page_count <= max_pages:
                    print(f"Scraping reviews from page {page_count}...")
                    review_elements = self.safe_find_elements(By.CSS_SELECTOR, review_selector)
                    print(f"Found {len(review_elements)} reviews on page {page_count}")
                    
                    for review in review_elements:
                        try:
                            review_data = {}
                            review_data['title'] = self.extract_text_safe(review.find_element(By.CSS_SELECTOR, ".review-title"))
                            review_data['text'] = self.extract_text_safe(review.find_element(By.CSS_SELECTOR, ".a-expander-content.reviewText.review-text-content.a-expander-partial-collapse-content"))
                            review_data['rating'] = self.extract_text_safe(review.find_element(By.CSS_SELECTOR, ".review-rating"))
                            review_data['customer_name'] = self.extract_text_safe(review.find_element(By.CSS_SELECTOR, "span.a-profile-name"))
                            review_data['helpful_votes'] = self.extract_text_safe(review.find_element(By.CSS_SELECTOR, ".a-size-small.a-color-secondary")) or "0 people found this helpful"
                            if review_data['text']:
                                reviews.append(review_data)
                        except Exception as e:
                            print(f"Error processing review on page {page_count}: {str(e)}")
                            continue
                    
                    # Check for 'Next page' button
                    next_page = self.safe_find_element(By.CSS_SELECTOR, "a[title='Next page'], li.a-last a")
                    if not next_page:
                        print(f"No more review pages found after page {page_count}")
                        break
                    
                    try:
                        next_page.click()
                        WebDriverWait(self.driver, 3).until(EC.staleness_of(next_page))
                        page_count += 1
                    except:
                        print(f"Could not click 'Next page' on page {page_count}")
                        break
                
            product_data['reviews'] = reviews
            print(f"Collected {len(reviews)} reviews across {page_count} pages")
            
            # 6. Brand Information
            product_data['brand'] = self.extract_text_safe(self.safe_find_element(By.ID, "bylineInfo"))
            
            # 7. Availability Status
            product_data['availability'] = self.extract_text_safe(self.safe_find_element(By.ID, "availability"))
            
            # 8. Product Variants
            variants = [self.extract_text_safe(v) for v in self.safe_find_elements(By.CSS_SELECTOR, "#variation_size_name li, #variation_color_name li") if self.extract_text_safe(v)]
            product_data['variants'] = variants
            
            # 9. Customer Questions & Answers
            qa_data = [self.extract_text_safe(qa) for qa in self.safe_find_elements(By.CSS_SELECTOR, "#ask-btf_feature_div .a-section")[:10] if self.extract_text_safe(qa)]
            product_data['qa'] = qa_data
            
            # 10. Related Products
            related_products = []
            for related in self.safe_find_elements(By.CSS_SELECTOR, "[data-automation-id='related-products'] a, #similarities a")[:10]:
                title = self.extract_attribute_safe(related, 'title')
                href = self.extract_attribute_safe(related, 'href')
                if title and href:
                    if not href.startswith('http'):
                        href = 'https://www.amazon.com' + href
                    related_products.append({'title': title, 'url': href})
            product_data['related_products'] = related_products
            
            # 11. Categories
            categories = [self.extract_text_safe(c) for c in self.safe_find_elements(By.ID, "wayfinding-breadcrumbs_feature_div") if self.extract_text_safe(c)]
            product_data['categories'] = categories
            
            # 12. Shipping Information
            shipping_info = [self.extract_text_safe(s) for s in self.safe_find_elements(By.ID, "mir-layout-DELIVERY_BLOCK") if self.extract_text_safe(s) and len(self.extract_text_safe(s)) > 5]
            product_data['shipping_info'] = shipping_info
            
            # 13. Best Seller Rank
            product_data['sales_rank'] = self.extract_text_safe(self.safe_find_element(By.ID, "SalesRank"))
            
            # 14. Concatenate text for RAG
            scraped_text = f"{product_data['title']}\n{product_data['features']}\n"
            for key, value in product_data['specifications'].items():
                scraped_text += f"{key}: {value}\n"
            for review in product_data['reviews']:
                scraped_text += f"Review by {review['customer_name']}: {review['title']} - {review['text']} (Rating: {review['rating']}, Helpful: {review['helpful_votes']})\n"
            for qa in product_data['qa']:
                scraped_text += f"Q&A: {qa}\n"
            product_data['scraped_text'] = scraped_text
            
            print("Data extraction completed successfully!")
            return product_data
            
        except Exception as e:
            print(f"Error occurred while scraping: {str(e)}")
            return None
        finally:
            if self.driver:
                self.driver.quit()

    def save_data_to_json(self, data, filename="product_data.json"):
        """Save scraped data to JSON file"""
        try:
            with open(filename, 'w', encoding='utf-8') as f:
                json.dump(data, f, ensure_ascii=False, indent=4)
            print(f"Data saved to {filename}")
        except Exception as e:
            print(f"Error saving data: {str(e)}")