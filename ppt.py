import streamlit as st, pandas as pd, json, time, re, hashlib, os, random, google.generativeai as genai
from datetime import datetime
from streamlit_autorefresh import st_autorefresh

STATE_FILE = "./challenge_state.json"
LEADERBOARD_FILE = "./leaderboard.json"
SUBMISSIONS_FILE = "./submissions.json"

def save_state(challenge_active=False, challenge_end_time=None):
    """Save the challenge state to a file"""
    with open(STATE_FILE, "w") as f:
        json.dump({
            "challenge_active": challenge_active,
            "challenge_end_time": challenge_end_time
        }, f)

def load_state():
    """Load challenge state from file"""
    if not os.path.exists(STATE_FILE):
        return False, None
    
    with open(STATE_FILE, "r") as f:
        try:
            data = json.load(f)
            return data.get("challenge_active", False), data.get("challenge_end_time")
        except:
            return False, None

def save_leaderboard(leaderboard_data):
    """Save leaderboard to file"""
    with open(LEADERBOARD_FILE, "w") as f:
        json.dump(leaderboard_data, f)

def load_leaderboard():
    """Load leaderboard from file"""
    if not os.path.exists(LEADERBOARD_FILE):
        save_leaderboard([])
        return []
    
    with open(LEADERBOARD_FILE, "r") as f:
        try:
            data = json.load(f)
            if not isinstance(data, list):
                data = []
                save_leaderboard(data)
            return data
        except Exception as e:
            print(f"Error loading leaderboard: {str(e)}")
            save_leaderboard([])
            return []

def save_submissions(submissions_data):
    """Save submissions to file"""
    try:
        directory = os.path.dirname(SUBMISSIONS_FILE)
        if directory and not os.path.exists(directory):
            os.makedirs(directory, exist_ok=True)
            
        with open(SUBMISSIONS_FILE, "w") as f:
            json.dump(submissions_data, f, default=str)  
            
        return True
    except Exception as e:
        print(f"Error saving submissions: {e}")
        return False

def load_submissions():
    """Load submissions from file"""
    if not os.path.exists(SUBMISSIONS_FILE):
        save_submissions({})
        return {}
    
    with open(SUBMISSIONS_FILE, "r") as f:
        try:
            data = json.load(f)
            if not isinstance(data, dict):
                data = {}
                save_submissions(data)
            return data
        except Exception as e:
            print(f"Error loading submissions: {str(e)}")
            save_submissions({})
            return {}

st.set_page_config(
    page_title="Prompt Battle Arena",
    page_icon="🥊",
    layout="wide",
    initial_sidebar_state="expanded",
    menu_items={
        'About': "# Prompt Battle Arena\nInteractive tool for prompt engineering practice and competition."
    }
)

st.markdown("""
<style>
    .main {
        background-color: #f5f7f9;
    }
    .stButton button {
        background-color: #4CAF50;
        color: white;
        font-weight: bold;
        border-radius: 5px;
        padding: 10px 24px;
        border: none;
    }
    .stButton button:hover {
        background-color: #45a049;
    }
    .css-1offfwp {border-radius: 10px;}
    .css-18e3th9 {padding-top: 2rem;}
    .challenge-card {
        background-color: white;
        padding: 20px;
        border-radius: 10px;
        box-shadow: 0 4px 8px rgba(0,0,0,0.1);
        margin-bottom: 20px;
    }
    .leaderboard {
        background-color: white;
        padding: 20px;
        border-radius: 10px;
        box-shadow: 0 4px 8px rgba(0,0,0,0.1);
    }
    .header {
        color: #1E3A8A;
        font-weight: bold;
    }
    .timer {
        font-size: 24px;
        font-weight: bold;
        color: #FF4B4B;
        text-align: center;
    }
    .admin-panel {
        background-color: #ffeeaa;
        padding: 15px;
        border-radius: 10px;
        border: 2px solid #ffcc00;
        margin-bottom: 20px;
    }
    .challenge-status {
        font-size: 18px;
        font-weight: bold;
        text-align: center;
        padding: 10px;
        border-radius: 5px;
        margin-bottom: 15px;
    }
    .status-active {
        background-color: #c8e6c9;
        color: #2e7d32;
    }
    .status-inactive {
        background-color: #ffcdd2;
        color: #c62828;
    }
    .waiting-screen {
        text-align: center;
        padding: 50px 20px;
        background-color: #e3f2fd;
        border-radius: 10px;
        margin-top: 50px;
    }
    .spinner {
        margin: 20px auto;
        width: 50px;
        height: 50px;
        border: 5px solid rgba(0, 0, 0, 0.1);
        border-radius: 50%;
        border-top-color: #3498db;
        animation: spin 1s ease-in-out infinite;
    }
    @keyframes spin {
        to { transform: rotate(360deg); }
    }
</style>
""", unsafe_allow_html=True)

data_extraction_challenge = {
    "name": "Advanced Multi-Format Data Extraction Challenge",
    "description": "Extract the following information from this complex invoice with inconsistent formatting as structured JSON: invoice number, date, total amount due, customer details (including all contact information), shipping information, all line items with their quantities, unit prices, SKU codes, and discounts. Calculate the accurate pre-tax subtotal and tax amount based on the line items.",
    "data": """
INVOICE #INV-20240328-9C45X
Issued: 03/28/2024    Due: Net-15    Terms: 2% \discount if paid within 7 days

BILLED TO:                         |  SHIP TO:
GlobalTech Solutions Inc.          |  GlobalTech Solutions - West Campus
Attn: Sarah Williams, Procurement  |  4588 Innovation Park, Building C
1250 Enterprise Boulevard          |  San Jose, CA 95132
Suite 300, Tower B                 |  Recipient: James Chen
Chicago, IL 60611                  |  Badge #: GT-2245
Tax ID: 81-3945027                 |  Contact: (408) 555-9087
sarah.w@globaltechsolutions.com    |  Delivery Instructions: Leave with security

ORDER REFERENCE: PO-GT-2024-0587
Sales Rep: Michael Johnson (ID: MJ394)
Customer Account: GLOB-ENT-7721

===================================================================================================
ITEM DESCRIPTION                           | SKU       | QTY |   UNIT PRICE  |  DISCOUNT  |  TOTAL
===================================================================================================
Enterprise Server Rack - 42U               | SVR-42U   |  2  |  $1,299.95    |    15%     | $2,209.92
---------------------------------------------------------------------------------------------------
High Performance SSD Storage Array         | SSD-HPE   |  3  |    $879.50    |     0%     | $2,638.50
---------------------------------------------------------------------------------------------------
Network Security Appliance - Advanced      | NSA-ADV   |  1  |  $3,295.00    |    7.5%    | $3,047.88
(Includes 12-month subscription)
---------------------------------------------------------------------------------------------------
Cat-7 Ethernet Cable Bundle (25 pcs)       | CAB-C7-25 |  4  |    $189.75    |    10%     |   $683.10
---------------------------------------------------------------------------------------------------
System Administration Software License     | SAS-ENT   |  2  |  $1,450.00    |     5%     | $2,755.00
(Enterprise Edition - 3 year)
---------------------------------------------------------------------------------------------------
Rack Mounting Kit - Universal              | RMK-UNV   |  8  |     $45.99    |     0%     |   $367.92
===================================================================================================

                                                                  Merchandise Subtotal: $11,702.32
                                                               Volume Discount (3.5%): -$409.58
                                                                   Adjusted Subtotal: $11,292.74
                                                                Shipping & Handling: $275.00
                                                                          Insurance: $150.00
                                                                     Processing Fee: $35.00
                                                                          Pre-tax Total: $11,752.74
                                                                  Sales Tax (8.25%): $969.60
                                                                     =====================
                                                                      ** TOTAL DUE: $12,722.34 **

PAYMENT METHODS:
- Bank Transfer: Account #7382910, Routing #021000089, First National Bank
- Credit Card: Please call (312) 555-3980 for secure processing
- Check: Payable to "TechSupply Distributors Inc."

NOTES:
1. All prices are in USD
2. Warranty information available at www.techsupply.com/warranty
3. Return policy: 30-day money-back guarantee for unopened items
4. Damaged items must be reported within 48 hours of delivery

TechSupply Distributors Inc.
2500 Commerce Parkway, Suite 400
Boston, MA 02110
Customer Service: (800) 555-8721
www.techsupply.com
""",
    "time_limit": 3 * 60,  
    "scoring_criteria": "Accuracy of extraction (completeness and correctness of all fields including nested structures), calculation accuracy, and correct handling of discounts and tax calculations. All numbers must match exactly with formatting preserved.",
    "expected_output": {
        "invoice_number": "INV-20240328-9C45X",
        "date": {
            "issued": "03/28/2024",
            "due": "Net-15",
            "payment_terms": "2% discount if paid within 7 days"
        },
        "customer": {
            "name": "GlobalTech Solutions Inc.",
            "attention": "Sarah Williams, Procurement",
            "address": {
                "street": "1250 Enterprise Boulevard",
                "suite": "Suite 300, Tower B",
                "city": "Chicago",
                "state": "IL",
                "zip": "60611"
            },
            "tax_id": "81-3945027",
            "email": "sarah.w@globaltechsolutions.com",
            "account": "GLOB-ENT-7721"
        },
        "shipping": {
            "name": "GlobalTech Solutions - West Campus",
            "address": {
                "street": "4588 Innovation Park, Building C",
                "city": "San Jose",
                "state": "CA",
                "zip": "95132"
            },
            "recipient": "James Chen",
            "badge": "GT-2245",
            "contact": "(408) 555-9087",
            "instructions": "Leave with security"
        },
        "order_reference": "PO-GT-2024-0587",
        "sales_rep": {
            "name": "Michael Johnson",
            "id": "MJ394"
        },
        "line_items": [
            {
                "description": "Enterprise Server Rack - 42U",
                "sku": "SVR-42U",
                "quantity": 2,
                "unit_price": "$1,299.95",
                "discount_percentage": 15,
                "total": "$2,209.92"
            },
            {
                "description": "High Performance SSD Storage Array",
                "sku": "SSD-HPE",
                "quantity": 3,
                "unit_price": "$879.50",
                "discount_percentage": 0,
                "total": "$2,638.50"
            },
            {
                "description": "Network Security Appliance - Advanced",
                "sku": "NSA-ADV",
                "quantity": 1,
                "unit_price": "$3,295.00",
                "discount_percentage": 7.5,
                "total": "$3,047.88",
                "notes": "Includes 12-month subscription"
            },
            {
                "description": "Cat-7 Ethernet Cable Bundle (25 pcs)",
                "sku": "CAB-C7-25",
                "quantity": 4,
                "unit_price": "$189.75",
                "discount_percentage": 10,
                "total": "$683.10"
            },
            {
                "description": "System Administration Software License",
                "sku": "SAS-ENT",
                "quantity": 2,
                "unit_price": "$1,450.00",
                "discount_percentage": 5,
                "total": "$2,755.00",
                "notes": "Enterprise Edition - 3 year"
            },
            {
                "description": "Rack Mounting Kit - Universal",
                "sku": "RMK-UNV",
                "quantity": 8,
                "unit_price": "$45.99",
                "discount_percentage": 0,
                "total": "$367.92"
            }
        ],
        "totals": {
            "merchandise_subtotal": "$11,702.32",
            "volume_discount": {
                "percentage": 3.5,
                "amount": "-$409.58"
            },
            "adjusted_subtotal": "$11,292.74",
            "shipping_and_handling": "$275.00",
            "insurance": "$150.00",
            "processing_fee": "$35.00",
            "pre_tax_total": "$11,752.74",
            "sales_tax": {
                "percentage": 8.25,
                "amount": "$969.60"
            },
            "total_due": "$12,722.34"
        },
        "payment_methods": [
            {
                "method": "Bank Transfer",
                "details": {
                    "account": "7382910",
                    "routing": "021000089",
                    "bank": "First National Bank"
                }
            },
            {
                "method": "Credit Card",
                "details": {
                    "phone": "(312) 555-3980",
                    "note": "for secure processing"
                }
            },
            {
                "method": "Check",
                "details": {
                    "payable_to": "TechSupply Distributors Inc."
                }
            }
        ],
        "notes": [
            "All prices are in USD",
            "Warranty information available at www.techsupply.com/warranty",
            "Return policy: 30-day money-back guarantee for unopened items",
            "Damaged items must be reported within 48 hours of delivery"
        ],
        "vendor": {
            "name": "TechSupply Distributors Inc.",
            "address": {
                "street": "2500 Commerce Parkway",
                "suite": "Suite 400",
                "city": "Boston",
                "state": "MA",
                "zip": "02110"
            },
            "customer_service": "(800) 555-8721",
            "website": "www.techsupply.com"
        }
    }
}

def setup_gemini_api(user_id=None):
    """Set up Gemini API with rotating API keys based on user ID"""
    if 'GEMINI_API_KEYS' in st.secrets:
        api_keys = st.secrets['GEMINI_API_KEYS']
        
        if not api_keys:
            st.error("No Gemini API keys configured in secrets.")
            return False
            
        if user_id:
            key_index = int(hashlib.md5(user_id.encode()).hexdigest(), 16) % len(api_keys)
        else:
            key_index = random.randint(0, len(api_keys) - 1)
            
        api_key = api_keys[key_index]
        genai.configure(api_key=api_key)
        return True
    else:
        try:
            genai.configure(api_key="DEMO_KEY")
            return True
        except:
            st.error("Gemini API keys not configured. This is a demo version.")
            return False

def call_gemini(prompt, challenge_data, user_id=None):
    try:
        api_configured = setup_gemini_api(user_id)
        
        full_prompt = f"""
        Data: {challenge_data['data']}
        
        {prompt}
        """
        
        if api_configured:
            try:
                model = genai.GenerativeModel('gemini-2.0-flash-lite')
                response = model.generate_content(
                    full_prompt,
                    generation_config=genai.types.GenerationConfig(
                        temperature=0.1,
                        top_p=0.95,
                        top_k=40,
                        candidate_count=1,
                        max_output_tokens=4096
                    )
                )
                return response.text
            except Exception as e:
                st.warning(f"API error: {e}. Using demo response.")
                return f"API error: {e}. Using demo response."
                
    except Exception as e:
        st.error(f"Error in call_gemini: {e}")
        return "Error generating response"

def evaluate_with_gemini(response, prompt, challenge, user_id=None):
    """Use Gemini API to evaluate and score the response based on challenge criteria"""
    try:
        api_configured = setup_gemini_api(user_id)
        
        evaluation_prompt = f"""
        You are an expert evaluator for advanced prompt engineering challenges specializing in data extraction. 
        Your task is to rigorously score a response on a scale of 0-100 based on how well it meets the requirements.
        
        CHALLENGE INFORMATION:

        Data provided:
        ```
        {challenge['data']}
        ```
        
        EXPECTED OUTPUT (GOLD STANDARD):
        ```
        {json.dumps(challenge['expected_output'], indent=2)}
        ```


        USER'S PROMPT:
        ```
        {prompt}
        ```
        
        MODEL'S RESPONSE TO THE PROMPT:
        ```
        {response}
        ```
        
        Please analyze the response with extreme attention to detail and assign a score from 0-100 based on these criteria:
        1. Completeness (20 points):
           - All required fields extracted (10 points)
           - Proper handling of nested structures (5 points)
           - No missing details from complex fields (5 points)
           
        2. Accuracy (40 points):
           - Correct extraction of all values (15 points)
           - Exact matching of numerical values with proper formatting (10 points)
           - Correct calculation of discounts and totals (10 points)
           - Proper handling of special formatting and notes (5 points)
           
        3. Structure (20 points):
           - JSON structure matches expected hierarchy (10 points)
           - Proper data types used throughout (5 points)
           - Consistent formatting and organization (5 points)
           
        4. Prompt Quality (20 points):
           - Clear instructions for handling complex formatting (5 points)
           - Specific guidance on nested structures (5 points)
           - Instructions for calculations and validation (5 points)
           - Effective strategies for ensuring data integrity (5 points)
        
        Deduct points severely for:
        - Missing or incorrect nested fields
        - Calculation errors in totals, discounts, or taxes
        - Improper handling of special characters and formatting
        - Structural errors in the JSON output
        - Missing notes or product details
        
        Return ONLY a JSON object with this structure:
        {{
            "total_score": <numerical_score_between_0_and_100>,
            "breakdown": {{
                "completeness": <score_out_of_20>,
                "accuracy": <score_out_of_40>,
                "structure": <score_out_of_20>,
                "prompt_quality": <score_out_of_20>
            }},
            "feedback": "<detailed explanation of the score with specific examples of errors or missing information, and suggestions for prompt improvement>"
        }}
        """
        
        if api_configured:
            try:
                model = genai.GenerativeModel('gemini-2.0-flash-lite')
                evaluation_response = model.generate_content(evaluation_prompt)
                
                json_match = re.search(r'\{.*\}', evaluation_response.text, re.DOTALL)
                if json_match:
                    result = json.loads(json_match.group(0))
                    return result
            except Exception as e:
                st.warning(f"API evaluation error: {e}. Using demo evaluation.")
                return {"error": f"API evaluation failed{e}, using demo evaluation."}
                
    except Exception as e:
        print(f"Evaluation error: {str(e)}")
        st.warning(f"Evaluation failed: {e}. Assigning default score.")
        return {
            "total_score": 65,
            "breakdown": {
                "completeness": 13,
                "accuracy": 26,
                "structure": 13,
                "prompt_quality": 13
            },
            "feedback": f"Evaluation error occurred. Default score assigned."
        }
 
def display_timer():
    challenge_active, challenge_end_time = load_state()
    
    if challenge_active and challenge_end_time:
        remaining = challenge_end_time - time.time()

        if remaining > 0:
            mins, secs = divmod(int(remaining), 60)
            st.markdown(f"<div class='timer'>⏳ Time Remaining: {mins:02d}:{secs:02d}</div>", unsafe_allow_html=True)
        else:
            st.markdown("<div class='timer'>⏰ Time's Up!</div>", unsafe_allow_html=True)
            
def start_challenge():
    end_time = time.time() + data_extraction_challenge["time_limit"]
    save_state(True, end_time)
    save_submissions({}) 
    save_leaderboard([]) 
    
def end_challenge():
    save_state(False, None)

def submit_prompt(user_id, user_name, user_prompt):
    challenge_active, challenge_end_time = load_state()
    
    if not user_name:
        st.error("Please enter your name before submitting")
        return False
        
    if challenge_end_time and time.time() > challenge_end_time:
        st.error("Time's up! You can't submit now.")
        return False
        
    submissions = load_submissions()
    
    if user_id in submissions:
        st.warning("You've already submitted a prompt for this challenge!")
        return False
        
        
    try:
        with st.spinner('Your prompt is being processed...'):
            response = call_gemini(user_prompt, data_extraction_challenge, user_id)
            
        with st.spinner('Evaluating response quality...'):
            evaluation = evaluate_with_gemini(response, user_prompt, data_extraction_challenge, user_id)
        
        if not isinstance(evaluation, dict) or "total_score" not in evaluation:
            evaluation = {
                "total_score": 50,
                "breakdown": {
                    "completeness": 10,
                    "accuracy": 20,
                    "structure": 10,
                    "prompt_quality": 10
                },
                "feedback": "Evaluation format error. Default score assigned."
            }
        
        submission_data = {
            "name": user_name,
            "prompt": user_prompt,
            "response": response,
            "evaluation": evaluation,
            "timestamp": datetime.now().isoformat()
        }
        
        submissions[user_id] = submission_data
        save_success = save_submissions(submissions)
        
        
        if not save_success:
            st.error("Failed to save your submission. Please try again.")
            return False
        
        leaderboard = load_leaderboard()
        
        new_entry = {
            'user_id': user_id,
            'name': user_name,
            'score': evaluation["total_score"],
            'timestamp': datetime.now().isoformat()
        }
        
        leaderboard.append(new_entry)
        save_leaderboard(leaderboard)
        
        print(f"Submission saved for {user_name} with score {evaluation['total_score']}")
        print(f"Updated leaderboard: {leaderboard}")
        
        st.success(f"Prompt submitted! Your score: {evaluation['total_score']}/100")
        return True
    except Exception as e:
        st.error(f"Error processing submission: {str(e)}")
        return False

def show_admin_page():
    st_autorefresh(interval=5000, key="admin-autorefresh")
    st.markdown("<h1 class='header'>🥊 Prompt Battle Arena - Admin Panel</h1>", unsafe_allow_html=True)
    
    challenge_active, challenge_end_time = load_state()
    
    st.markdown("<div class='admin-panel'>", unsafe_allow_html=True)
    
    status_class = "status-active" if challenge_active else "status-inactive"
    status_text = "CHALLENGE ACTIVE" if challenge_active else "CHALLENGE INACTIVE"
    st.markdown(f"<div class='challenge-status {status_class}'>{status_text}</div>", unsafe_allow_html=True)
    
    if challenge_active:
        display_timer()
    
    col1, col2 = st.columns(2)
    with col1:
        start_btn = st.button("Start Challenge", key="start", disabled=challenge_active)
        if start_btn:
            start_challenge()
            st.success("Challenge has started!")
            st.rerun()
    with col2:
        end_btn = st.button("End Challenge", key="end", disabled=not challenge_active)
        if end_btn:
            end_challenge()
            st.rerun()
            
    st.markdown("</div>", unsafe_allow_html=True)
    
    with st.container():
        st.markdown(f"**Scoring Criteria:**  \n{data_extraction_challenge['scoring_criteria']}")
        st.markdown("</div>", unsafe_allow_html=True)
    
    with st.expander("Debug Info (Submissions & Leaderboard)"):
        st.write("Current Submissions:")
        st.json(load_submissions())
        st.write("Current Leaderboard:")
        st.json(load_leaderboard())
    
    with st.container():
        st.markdown("<div class='leaderboard'>", unsafe_allow_html=True)
        st.subheader("📊 Leaderboard")
        
        leaderboard = load_leaderboard()
        submissions = load_submissions()
        
        if leaderboard:
            try:
                leaderboard_df = pd.DataFrame(leaderboard)
                
                top_entries = leaderboard_df.sort_values('score', ascending=False)
                
                st.dataframe(
                    top_entries[['name', 'score', 'timestamp']].rename(columns={
                        'name': 'Name', 
                        'score': 'Score', 
                        'timestamp': 'Timestamp'
                    }),
                    hide_index=True,
                    use_container_width=True
                )
            
                if len(top_entries) >= 1:
                    st.write("**Top Prompt:**")
                    top_user_id = top_entries.iloc[0]['user_id']
                    top_name = top_entries.iloc[0]['name']
                    top_score = top_entries.iloc[0]['score']
                    st.info(f"**{top_name}** - Score: {top_score}")
                    
                    if top_user_id in submissions:
                        sub = submissions[top_user_id]
                        with st.expander("View Winning Prompt"):
                            st.write(sub["prompt"])
                        with st.expander("View Response"):
                            st.write(sub["response"])
                        with st.expander("View Evaluation"):
                            st.json(sub["evaluation"])
            except Exception as e:
                st.error(f"Error displaying leaderboard: {str(e)}")
        else:
            st.write("No submissions yet.")
        
        st.markdown("</div>", unsafe_allow_html=True)

def show_user_page(username, user_id):
    
    st.markdown("<h1 class='header'>🥊 Prompt Battle Arena</h1>", unsafe_allow_html=True)
    
    challenge_active, challenge_end_time = load_state()
    
    if not challenge_active:
        st.warning("Waiting for the admin to start the challenge...")
        st_autorefresh(interval=5000, key="user-autorefresh")
        st.markdown("<div class='waiting-screen'>", unsafe_allow_html=True)
        st.markdown("<h2>Waiting for the challenge to start...</h2>", unsafe_allow_html=True)
        st.markdown("<div class='spinner'></div>", unsafe_allow_html=True)
        st.markdown("<p>Please wait until the administrator starts the challenge.</p>", unsafe_allow_html=True)
        st.markdown("</div>", unsafe_allow_html=True)
        
        if st.button("Refresh"):
            st.rerun()
    else:
        with st.container():
            st.markdown("<div class='challenge-card'>", unsafe_allow_html=True)
            
            st.markdown(f"<h2>{data_extraction_challenge['name']}</h2>", unsafe_allow_html=True)
            
            display_timer()
            
        
            st.markdown("**Data:**")
            st.code(data_extraction_challenge['data'], language="text")
            
            st.markdown("**Expected Output Format Example:**")
            st.json({
                "invoice_number": "example",
                "date": "example date",
                "customer_name": "example name",
                "total_amount": "$000.00",
                "line_items": [
                    {"product": "item name", "quantity": 0, "unit_price": "$0.00", "total": "$0.00"}
                ]
            })
            
            submissions = load_submissions()
            
            time_is_up = challenge_end_time and time.time() > challenge_end_time
            
            if user_id not in submissions and not time_is_up:
                user_name = st.text_input("Your Name:", value=username)
                user_prompt = st.text_area("Write your prompt here:", 
                             help="Create a prompt that will instruct the AI to extract data from the invoice in the correct format.",
                             height=150,
                             placeholder="Write a detailed prompt that will make the AI extract the invoice data correctly...")
                
                submit_button = st.button("Submit Prompt")
                if submit_button:
                    success = submit_prompt(user_id, user_name, user_prompt)
                    if success:
                        st.rerun()
            else:
                if user_id in submissions:
                    sub = submissions[user_id]
                    eval_result = sub["evaluation"]
                    
                    st.success(f"Your submission has been received! Your score: {eval_result['total_score']}/100")
                    
                    col1, col2 = st.columns(2)
                    with col1:
                        with st.expander("Your Prompt"):
                            st.write(sub["prompt"])
                        
                        with st.expander("AI Response"):
                            st.code(sub["response"], language="json")
                    
                    with col2:
                        with st.expander("Score Breakdown"):
                            for category, score in eval_result["breakdown"].items():
                                st.markdown(f"**{category.title()}**: {score} points")
                        
                        with st.expander("Feedback"):
                            st.write(eval_result["feedback"])
                elif time_is_up:
                    st.error("Time's up! You can no longer submit a prompt for this challenge.")
            
            st.markdown("</div>", unsafe_allow_html=True)
            
def main():
    setup_gemini_api()
    
    if not os.path.exists(STATE_FILE):
        save_state(False, None)
    if not os.path.exists(LEADERBOARD_FILE):
        save_leaderboard([])
    if not os.path.exists(SUBMISSIONS_FILE):
        save_submissions({})
    
    if 'username_input' not in st.session_state:
        st.session_state.username_input = ""
    
    if 'user_id' not in st.session_state:
        session_id = str(time.time())
        st.session_state.user_id = hashlib.md5(session_id.encode()).hexdigest()
    
    params = st.experimental_get_query_params()
    is_admin = params.get('admin', [''])[0] == 'true'
    
    st.sidebar.title("🥊 Prompt Battle Arena")
    
    if not is_admin:
        admin_expander = st.sidebar.expander("Admin Access")
        with admin_expander:
            admin_password = st.text_input("Admin Password", type="password", key="admin_pwd")
            admin_login = st.button("Login as Admin")
            if admin_login and admin_password == "admin123":  
                st.experimental_set_query_params(admin='true')
                st.rerun()
    
    if is_admin:
        st.sidebar.success("Logged in as Admin")
        logout_button = st.sidebar.button("Logout")
        if logout_button:
            st.experimental_set_query_params()
            st.rerun()
        show_admin_page()
    else:
        if not st.session_state.username_input:
            st.session_state.username_input = st.sidebar.text_input("Enter Your Name:")
        
        show_user_page(st.session_state.username_input, st.session_state.user_id)

if __name__ == "__main__":
    main()