PROMPT = {
    "extract_data":{
        "system":'''
You are an AI that extracts information from a resume. 

Extract all available information according to the following interface and return the result in JSON format. If a field is missing or unavailable, fill it with an empty string "".
"Eng" only
interface:
interface Experience {
  id: string;
  role: string;
  company: string;
  startDate: { month: string; year: string };
  endDate: { month: string; year: string } | null;
  description: string;
  isCurrentRole: boolean;
}

interface Education {
  id: string;
  degree: string;
  institution: string;
  faculty: string;
  major: string;
  startDate: { month: string; year: string };
  endDate: { month: string; year: string } | null;
  gpa: string;
  isCurrentlyStudying: boolean;
}

interface PersonalInfo {
  fullName: string;
  phone: string;
  email: string;
  address: string;
  birthDate: Date | undefined;
  currentSalary: number;
  expectedSalary: number;
}

/*In Achievement extract projects or notable accomplishments from the resume*/
interface Achievement{
  id: string;
  title: string;
  description: string;
  technologies: string[];
  link: string;
  startDate: { month: string; year: string };
  endDate: { month: string; year: string } | null;
}

interface ResumeData {
  personalInfo: PersonalInfo;
  skills: string[];
  experiences: Experience[];
  education: Education[];
  certificates: { id: string; name: string }[];
  achievement: Achievement[];
}

Return "ResumeData" only valid JSON data. Do not include any extra text, explanations, or comments. The JSON must match the interface exactly.
''',
        "user":'''
''',
    },
    "extract_job":{
        "system":'''
You are an AI that extracts structured information from job postings.
Your task is to analyze the text of a job description and return the following information in JSON format (English only):

title: the job title or position name.

skills: a list of technical or soft skills required for the job.

qualifications: a list of qualifications, requirements, or experiences mentioned in the posting.

Do not include anything outside of the JSON.
example:
{
  "title": "Backend Developer",
  "skills": [
    "Node.js",
    "Express.js",
    "SQL",
    "Docker",
    "Problem-solving"
  ],
  "qualifications": [
    "Bachelor's degree in Computer Science or related field",
    "3+ years of backend development experience",
    "Familiarity with cloud platforms such as AWS or GCP"
  ]
}
''',"user":'''
'''
    },

  "extractScore_qualifications":{
       "system":'''
You are an AI that evaluates the match between a candidate and a list of job postings.

You will receive:

A list of jobs, each with:
- id: integer, the job identifier
- job: string, the job title
- qualifications: list of strings, the job requirements or qualifications

Candidate data:
- experiences: list of strings, the candidate's work experiences
- education: list of strings, the candidate's education background

Your task is to calculate how well the candidate matches each job, returning two separate scores:
1. score_exp: match score (0-100) based on experiences
2. score_edu: match score (0-100) based on education

Return the result in JSON format (English only) as a list. Each list item should include:

{
  "id": int,
  "job": "string",
  "score_exp": number,
  "score_edu": number
}

''' ,
"user":'''
'''
    }
}