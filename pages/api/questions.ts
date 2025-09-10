import { NextApiRequest, NextApiResponse } from 'next';
import fs from 'fs';
import path from 'path';

const questionsPath = path.join(process.cwd(), 'generated_questions.json');

export default function handler(req: NextApiRequest, res: NextApiResponse) {
  try {
    if (req.method === 'GET') {
      // Read generated questions
      if (!fs.existsSync(questionsPath)) {
        return res.status(200).json({ questions: [] });
      }
      
      const data = fs.readFileSync(questionsPath, 'utf8');
      const questions = JSON.parse(data);
      return res.status(200).json(questions);
      
    } else if (req.method === 'DELETE') {
      // Remove a specific question
      const { question } = req.body;
      
      if (!fs.existsSync(questionsPath)) {
        return res.status(404).json({ error: 'Questions file not found' });
      }
      
      const data = fs.readFileSync(questionsPath, 'utf8');
      const questionsData = JSON.parse(data);
      
      questionsData.questions = questionsData.questions.filter((q: string) => q !== question);
      
      fs.writeFileSync(questionsPath, JSON.stringify(questionsData, null, 2));
      return res.status(200).json({ message: 'Question removed successfully' });
      
    } else if (req.method === 'POST') {
      // Add a new question
      const { question } = req.body;
      
      let questionsData;
      if (fs.existsSync(questionsPath)) {
        const data = fs.readFileSync(questionsPath, 'utf8');
        questionsData = JSON.parse(data);
      } else {
        questionsData = { questions: [] };
      }
      
      questionsData.questions.push(question);
      
      fs.writeFileSync(questionsPath, JSON.stringify(questionsData, null, 2));
      return res.status(200).json({ message: 'Question added successfully' });
      
    } else {
      res.setHeader('Allow', ['GET', 'POST', 'DELETE']);
      return res.status(405).end(`Method ${req.method} Not Allowed`);
    }
  } catch (error) {
    console.error('Questions API error:', error);
    return res.status(500).json({ error: 'Internal server error' });
  }
}