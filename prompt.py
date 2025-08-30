PROMPT = {
    "extract_data":{
        "system":'''
You are an AI that extracts information from a resume. 

Extract all available information according to the following interface and return the result in JSON format. If a field is missing or unavailable, fill it with an empty string "".
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
    }
}