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
Analyze the text of a job description and return the following information in JSON format (English only):
title: the job title or position name.
skills: a list of technical or soft skills required for the job. Include full names of frameworks, libraries, platforms, and tools (e.g., “Next.js”, “Express.js”, “React”, “AWS”).
qualifications: a list of qualifications, requirements, or experiences mentioned in the posting.
Requirements:
Only include skills and qualifications explicitly mentioned in the job description.
Use the exact wording for technical tools, frameworks, and programming languages.
Do not include inferred or assumed skills.
Return only valid JSON.
Example output:
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

job_data :
A list of jobs, each with:
- id: integer, the job identifier
- job: string, the job title
- qualifications: list of strings, the job requirements or qualifications

Candidate_data: 
- experiences: list of strings, the candidate's work experiences
- education: list of strings, the candidate's education background
- achievements: list of strings, the candidate's achievements or projects

Your task is to calculate how well the candidate matches each job, returning the following:

1. score_exp: match score (0-100) based on experiences
2. score_edu: match score (0-100) based on education
3. score_ach: match score (0-100) based on achievements/projects
4. exp_reasons: a list of objects that show comparisons between job requirements and candidate experiences.  
   Each object must have:
   - job: the requirement from the job
   - candidate: the most relevant candidate experience (or "missing" if none found)
   - isMatch: true if the candidate meets the requirement, false otherwise
5. edu_reasons: a list of objects that show comparisons between job requirements and candidate education.  
   Each object must have:
   - job: the requirement from the job
   - candidate: the most relevant candidate education (or "missing" if none found)
   - isMatch: true if the candidate meets the requirement, false otherwise
6. ach_reasons: a list of objects that show how the candidate's achievements/projects relate to the job requirements.  
   Each object must have:
   - job: the requirement from the job
   - candidate: the most relevant candidate achievement/project (or "missing" if none found)
   - reason: explanation of why it matches or is relevant

Return the result in JSON format (English only) as a list. Each list item should include:

{
  "id": int,
  "job": "string",
  "score_exp": number,
  "score_edu": number,
  "score_ach": number,
  "exp_reasons": [
    {"job": "string", "candidate": "string", "isMatch": bool},
    ...
  ],
  "edu_reasons": [
    {"job": "string", "candidate": "string", "isMatch": bool},
    ...
  ],
  "ach_reasons": [
    {"job": "string", "candidate": "string", "reason": "string"},
    ...
  ]
}

''' ,
"user":'''
'''
    }
}