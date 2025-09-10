import { NextApiRequest, NextApiResponse } from 'next';
import fs from 'fs';
import path from 'path';

const invalidQuestionsPath = path.join(process.cwd(), 'invalid_questions.json');

export default function handler(req: NextApiRequest, res: NextApiResponse) {
  try {
    if (req.method === 'GET') {
      // Read invalid questions
      if (!fs.existsSync(invalidQuestionsPath)) {
        return res.status(200).json({ invalid_questions: [] });
      }
      
      const data = fs.readFileSync(invalidQuestionsPath, 'utf8');
      const questions = JSON.parse(data);
      return res.status(200).json(questions);
      
    } else if (req.method === 'POST') {
      // Add an invalid question
      const invalidQuestion = req.body;
      
      let questionsData;
      if (fs.existsSync(invalidQuestionsPath)) {
        const data = fs.readFileSync(invalidQuestionsPath, 'utf8');
        questionsData = JSON.parse(data);
      } else {
        questionsData = { invalid_questions: [] };
      }
      
      questionsData.invalid_questions.push(invalidQuestion);
      
      fs.writeFileSync(invalidQuestionsPath, JSON.stringify(questionsData, null, 2));
      return res.status(200).json({ message: 'Invalid question added successfully' });
      
    } else {
      res.setHeader('Allow', ['GET', 'POST']);
      return res.status(405).end(`Method ${req.method} Not Allowed`);
    }
  } catch (error) {
    console.error('Invalid questions API error:', error);
    return res.status(500).json({ error: 'Internal server error' });
  }
}