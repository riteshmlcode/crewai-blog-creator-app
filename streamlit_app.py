from crewai import Agent, Task, Crew, LLM
from crewai_tools import SerperDevTool
import streamlit as st
from dotenv import load_dotenv
import os

load_dotenv()

os.environ['GEMINI_API_KEY'] = os.getenv("GEMINI_API_KEY")

llm=LLM(
    model=os.getenv("GEMINI_LLM_MODEL"),
    verbose=True,
    google_api_key=os.getenv("GEMINI_API_KEY"),

)
# Streamlit Page Config
st.set_page_config(page_title="Content Researcher & Writer", page_icon="@@", layout="wide")

# Title and Description
st.title("Content Researcher and Writer,Yubi")
st.markdown("Generate blog posts about any topics using AI Agents.")

# Sidebar
with st.sidebar:
    st.header("Content Settings")

    # Make the text input 
    topic = st.text_area(
        "Enter the Topic",
        height=100,
        placeholder="Enter the Topic"
    )

    # Add more sidebar controls
    st.markdown("LLM Settings")
    temperature = st.slider("Temparature", 0.0, 1.0, 0.7)

    # Add some spacing
    st.markdown("---")

    # Make the generate button more prominent in the sidebar
    generate_button = st.button("Generate Content", type="primary", use_container_width=True)

    # Add some helpful information
    with st.expander("How to Use"):
        st.markdown("""
        1. Enter your desired content topic
        2. Play with the temperature
        3. Click 'Generate Content' to start
        4. Wait for the AI to generate your article
        5. Download the result as a markdown file
        """)

def generate_content(topic):
    # llm = LLM(model="gemini-1.5-flash-002")

    # Tool 2
    search_tool = SerperDevTool(n=10)

    # Agent 1
    senior_research_analyst = Agent(
        role = "Senior Research Analyst",
        goal = f"Research, analyze and synthesize comprehensive information on {topic} from reliable web sources",
        backstory = "You are an expert research analyst with advanced web research skills."
                    "You excel at finding, analyzing and synthesizing information from "
                    "across the internet using search tools. You are skilled at distinguishing reliable"
                    "sources from unreliable onces, fact-checking, cross-referencing information, and"
                    "identifying key patterns and insights. You provide well-organized research briefs with"
                    "proper citations and source verification. Your analysis includes both raw data and"
                    "interpreted insights, making complex information accessible and actionable",
        allow_delegation = False,
        verbose = True,
        tools = [search_tool],
        llm = llm
    )

    # Agent 2: Content Writer

    content_writer = Agent(
        role = "Content Writer",
        goal = "Transform research findings into engaging blog posts where maintaining accuracy",
        backstory = "You are a skilled content writer specialized in creating"
                    "engaging, accessible content from technical research. "
                    "You work closely with the Senior Research Analyst and exel at maintaining the perfect"
                    "balance between informative and entertaining writing, while ensuring all facts and citations from"
                    "research are properly incorporated. You have a talent for making complex topics approachable"
                    "withoyt oversimplifying them.",
        allow_delegation = False,
        verbose = True,
        llm = llm    
    )

    # Research Tasks

    research_tasks = Task(
        description = ("""
                1. Conduct comprehensive research on {topic} including:
                    - Recent developments and news
                    - Key industry trends and innovations
                    - Expert opinions and analysis
                    - Statistical data and market insights
                2. Evaluate source credibility and fact-check all information
                3. Organize findings into a structured research brief
                4. Include all relevant citations and sources
        """),
        expected_output = """A detailed research report containing:
                    - Executive summary of key findings
                    - Comprehensive analysis of current trends and developments
                    - List of verified facts and statistics
                    - All citations and links to origin sources
                    - Clear categorization of main themes and patterns
                     Please format with clear sections and bullet points for easy reference.""",
        agent = senior_research_analyst
    )

    # Task 2: Content Writing 

    writing_task = Task(
        description = ("""
            Using the research brief provided, create an engaging blog post that :
            1. Transforms technical information into accessible content
            2. Maintains all factual accuracy and citations from teh research
            3. Includes:
                - Attention-grabbing Introduction
                - Well-structured body sections with clear headings
                - Compelling conclusion
            4. Preserces all source citations in [Source: URL] format
            5. Includes a reference section at the end
        """),
        expected_output = """A polished blog post in markdown format that:
            - Engages readers while maintaining accuracy
            - Contains properly structured sections
            - Includes Inline citations hyperlinked to the origin source url
            - Presents information in an accessible yet informative way
            - Follows proper markdown formatting, use H1 for the title and H3 for the sub-sections""",
        agent = content_writer
    )

    crew = Crew(
        agents = [senior_research_analyst, content_writer],
        tasks = [research_tasks, writing_task],
        verbose = True
    )

    return crew.kickoff(inputs= {"topic" : topic})

# Main Content Area
if generate_button:
    with st.spinner('Generating Content ....This may take a moment.'):
        try:
            result = generate_content(topic)
            st.markdown("### Generated Content")
            st.markdown(result)

            # Add a download button
            st.download_button(
                label="Download Content",
                data=result.raw,
                file_name=f"{topic.lower().replace(' ','_')}_article.md",
                mime="text/markdown"
            )
        except Exception as e:
            st.error(f"An error occured:{str(e)}")
#Footer
st.markdown("---")
st.markdown("Built with CrewAI,Streamlit and Gemini")