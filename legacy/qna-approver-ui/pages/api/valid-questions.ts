import { NextApiRequest, NextApiResponse } from 'next';
import fs from 'fs';
import path from 'path';

const validQuestionsPath = path.join(process.cwd(), 'valid_questions.json');

export default function handler(req: NextApiRequest, res: NextApiResponse) {
  try {
    if (req.method === 'GET') {
      // Read valid questions
      if (!fs.existsSync(validQuestionsPath)) {
        return res.status(200).json({ valid_questions: [] });
      }
      
      const data = fs.readFileSync(validQuestionsPath, 'utf8');
      const questions = JSON.parse(data);
      return res.status(200).json(questions);
      
    } else if (req.method === 'POST') {
      // Add a validated question
      const validatedQuestion = req.body;
      
      let questionsData;
      if (fs.existsSync(validQuestionsPath)) {
        const data = fs.readFileSync(validQuestionsPath, 'utf8');
        questionsData = JSON.parse(data);
      } else {
        questionsData = { valid_questions: [] };
      }
      
      questionsData.valid_questions.push(validatedQuestion);
      
      fs.writeFileSync(validQuestionsPath, JSON.stringify(questionsData, null, 2));
      return res.status(200).json({ message: 'Valid question added successfully' });
      
    } else {
      res.setHeader('Allow', ['GET', 'POST']);
      return res.status(405).end(`Method ${req.method} Not Allowed`);
    }
  } catch (error) {
    console.error('Valid questions API error:', error);
    return res.status(500).json({ error: 'Internal server error' });
  }
}