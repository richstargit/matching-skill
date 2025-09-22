PROMPT = {
    "extract_data":{
        "system":'''
You are an AI that extracts information from a resume.

Extract all available information according to the following interface and return the result in JSON format. If a field is missing or unavailable, fill string data with an empty string "" and number data with 0.
All data should be in English.

Important:
For skill
- skills: a list of hard skills only (technical skills, tools, frameworks, libraries, platforms, programming languages).
- Always use names can identify (e.g., "Golang", "Express.js", "React").
- Do not use abbreviations alone (e.g., "Go" → "Golang", "Express" → "Express.js").

For the Education interface, if the degree contains the major (e.g., "Bachelor of Computer Science"), separate it properly:
-degree: "Bachelor"
-major: "Computer Science"

For Experience:
- Separate the level (e.g., "junior", "senior" lower all) into the role field. Example: if the title is "Senior Software Engineer", then role: "Software Engineer" and an additional field "level": "Senior".
- If no level is provided, set "level": "".

interface definitions:

interface Experience {
  id: int;
  role: string;
  level: string;
  company: string;
  startDate: { month: string; year: string };
  endDate: { month: string; year: string } | null;
  description: string;
  isCurrentRole: boolean;
}

interface Education {
  id: int;
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

interface Achievement {
  id: int;
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
  certificates: { id: int; name: string }[];
  achievement: Achievement[];
}

Return only valid JSON of ResumeData matching the interface exactly.
Do not include extra text, explanations, or comments.
''',
        "user":'''
''',
    },
    "extract_job":{
        "system":'''
You are an AI that extracts structured information from job postings.
Analyze the text of a job description and return the following information in JSON format (English only):
Extraction rules:
- title: the job title or position name.
- skills: a list of hard skills only (technical skills, tools, frameworks, libraries, platforms, programming languages).
  - Always use names can identify (e.g., "Golang", "Express.js", "React").
  - Do not use abbreviations alone (e.g., "Go" → "Golang", "Express" → "Express.js").
- experiences: a list of required work experiences (position role) and find experience year if not find give 0. Each item must have the format:
  {
    "job_name": "Position or role (if multiple roles separated by 'or', create a new entry for each)",
    "level": "e.g., Junior, Senior (if not specified, use empty string '')",
    "min_experience_years": 0,
    "max_experience_years": 0,
    "description": "Experience requirement text from the JD"
  }
  - If only a minimum is provided (e.g., "3+ years"), set "max_experience_years": null.
  - If a range is given (e.g., "3–5 years"), fill both min and max.
  Special rules for experience:
  - If both "Junior" and "Senior" are mentioned for the same role with different minimum years, 
    then combine them into a single record:
    - Set "min_experience_years" = the minimum for Junior.
    - Set "max_experience_years" = the minimum for Senior.

- educations: a list of required education qualifications and id number only. Each item must have the format:
  {
    "id": 1,
    "education": ["Exact degree field(s). If the JD says 'or related field', replace with 3–5 most relevant academic fields instead of keeping the phrase"],
    "minimum_level": ["Bachelor's degree" , "Master's degree" , "High School", "etc."]
  }
- responsibilities: a list of job duties and responsibilities as plain text.

Requirements:
- Only include information explicitly mentioned in the job description.
- Do not infer or assume skills, experiences, or educations not written in the JD.
- Use the exact wording from the JD where applicable, except for replacing "or related field" with 3–5 real academic fields.
- Return only valid JSON.
Example output:
{
  "title": "Backend Developer",
  "skills": [
    "Node.js",
    "Express.js",
    "SQL",
    "Docker",
    "AWS"
  ],
  "experiences": [
    {
      "job_name": "Backend Developer",
      "level" : "senior"
      "min_experience_years": 3,
      "max_experience_years": null,
      "description": "3+ years of backend development experience"
    }
  ],
  "educations": [
    {
      "id": 1,
      "education": ["Computer Science", "Software Engineering", "Information Technology", "Computer Engineering"],
      "minimum_level": "Bachelor's degree"
    }
  ],
  "responsibilities": [
    "Develop and maintain backend services",
    "Design and optimize database queries",
    "Deploy applications on cloud infrastructure"
  ]
}
Now extract from this job description:
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