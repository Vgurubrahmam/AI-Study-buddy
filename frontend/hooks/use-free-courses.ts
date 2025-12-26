"use client"

import { useState, useEffect, useCallback } from "react"

// Course interface for normalized data
export interface Course {
  id: string
  title: string
  description: string
  provider: string
  url: string
  imageUrl?: string
  level: "Beginner" | "Intermediate" | "Advanced"
  rating?: number
  students?: number
  duration?: string
  category: string
  isFree: boolean
}

// Enrolled courses storage
const ENROLLED_COURSES_KEY_PREFIX = "enrolled_courses_"
const COURSE_PROGRESS_KEY_PREFIX = "course_progress_"

function getUserId(): string | null {
  try {
    const userStr = localStorage.getItem("user")
    if (userStr) {
      const user = JSON.parse(userStr)
      return user._id || user.id || null
    }
  } catch {
    return null
  }
  return null
}

function getEnrolledKey(): string {
  const userId = getUserId()
  return userId ? `${ENROLLED_COURSES_KEY_PREFIX}${userId}` : `${ENROLLED_COURSES_KEY_PREFIX}guest`
}

function getProgressKey(): string {
  const userId = getUserId()
  return userId ? `${COURSE_PROGRESS_KEY_PREFIX}${userId}` : `${COURSE_PROGRESS_KEY_PREFIX}guest`
}

// Free course APIs we'll use
const COURSE_APIS = {
  // Free Code Camp courses (simulated structure)
  freeCodeCamp: "https://www.freecodecamp.org/news/ghost/api/v3/content/posts/?key=&limit=10",
  // Open Library for educational books
  openLibrary: "https://openlibrary.org/subjects/",
}

// Simulated real-time course data from various free platforms
// In production, these would be fetched from actual APIs
const fetchFreeCourses = async (): Promise<Course[]> => {
  // Simulate API delay
  await new Promise(resolve => setTimeout(resolve, 500))
  
  const courses: Course[] = [
    // Programming courses
    {
      id: "fcc-responsive-web",
      title: "Responsive Web Design Certification",
      description: "Learn HTML, CSS, Flexbox, CSS Grid, and build responsive websites",
      provider: "freeCodeCamp",
      url: "https://www.freecodecamp.org/learn/responsive-web-design/",
      imageUrl: "https://cdn.freecodecamp.org/platform/universal/fcc_meta_1920X1080-indigo.png",
      level: "Beginner",
      rating: 4.8,
      students: 450000,
      duration: "300 hours",
      category: "Web Development",
      isFree: true,
    },
    {
      id: "fcc-javascript",
      title: "JavaScript Algorithms and Data Structures",
      description: "Master JavaScript fundamentals, ES6, regex, debugging, and algorithms",
      provider: "freeCodeCamp",
      url: "https://www.freecodecamp.org/learn/javascript-algorithms-and-data-structures/",
      imageUrl: "https://cdn.freecodecamp.org/platform/universal/fcc_meta_1920X1080-indigo.png",
      level: "Intermediate",
      rating: 4.9,
      students: 380000,
      duration: "300 hours",
      category: "Programming",
      isFree: true,
    },
    {
      id: "fcc-frontend-libs",
      title: "Front End Development Libraries",
      description: "Learn React, Redux, Sass, Bootstrap, and jQuery",
      provider: "freeCodeCamp",
      url: "https://www.freecodecamp.org/learn/front-end-development-libraries/",
      imageUrl: "https://cdn.freecodecamp.org/platform/universal/fcc_meta_1920X1080-indigo.png",
      level: "Intermediate",
      rating: 4.7,
      students: 290000,
      duration: "300 hours",
      category: "Web Development",
      isFree: true,
    },
    {
      id: "fcc-python",
      title: "Scientific Computing with Python",
      description: "Learn Python fundamentals, data structures, and scientific computing",
      provider: "freeCodeCamp",
      url: "https://www.freecodecamp.org/learn/scientific-computing-with-python/",
      imageUrl: "https://cdn.freecodecamp.org/platform/universal/fcc_meta_1920X1080-indigo.png",
      level: "Beginner",
      rating: 4.8,
      students: 320000,
      duration: "300 hours",
      category: "Programming",
      isFree: true,
    },
    {
      id: "fcc-data-analysis",
      title: "Data Analysis with Python",
      description: "Learn data analysis with Pandas, NumPy, Matplotlib, and Seaborn",
      provider: "freeCodeCamp",
      url: "https://www.freecodecamp.org/learn/data-analysis-with-python/",
      imageUrl: "https://cdn.freecodecamp.org/platform/universal/fcc_meta_1920X1080-indigo.png",
      level: "Intermediate",
      rating: 4.7,
      students: 180000,
      duration: "300 hours",
      category: "Data Science",
      isFree: true,
    },
    {
      id: "fcc-machine-learning",
      title: "Machine Learning with Python",
      description: "Build neural networks and ML models using TensorFlow",
      provider: "freeCodeCamp",
      url: "https://www.freecodecamp.org/learn/machine-learning-with-python/",
      imageUrl: "https://cdn.freecodecamp.org/platform/universal/fcc_meta_1920X1080-indigo.png",
      level: "Advanced",
      rating: 4.6,
      students: 150000,
      duration: "300 hours",
      category: "Machine Learning",
      isFree: true,
    },
    // Khan Academy courses
    {
      id: "khan-algebra",
      title: "Algebra Fundamentals",
      description: "Master algebraic expressions, equations, and functions",
      provider: "Khan Academy",
      url: "https://www.khanacademy.org/math/algebra",
      imageUrl: "https://cdn.kastatic.org/images/khan-logo-dark-background.png",
      level: "Beginner",
      rating: 4.9,
      students: 890000,
      duration: "40 hours",
      category: "Mathematics",
      isFree: true,
    },
    {
      id: "khan-calculus",
      title: "Calculus 1",
      description: "Learn limits, derivatives, and integrals",
      provider: "Khan Academy",
      url: "https://www.khanacademy.org/math/calculus-1",
      imageUrl: "https://cdn.kastatic.org/images/khan-logo-dark-background.png",
      level: "Intermediate",
      rating: 4.8,
      students: 560000,
      duration: "60 hours",
      category: "Mathematics",
      isFree: true,
    },
    {
      id: "khan-physics",
      title: "Physics",
      description: "Explore mechanics, thermodynamics, and electromagnetism",
      provider: "Khan Academy",
      url: "https://www.khanacademy.org/science/physics",
      imageUrl: "https://cdn.kastatic.org/images/khan-logo-dark-background.png",
      level: "Intermediate",
      rating: 4.7,
      students: 420000,
      duration: "80 hours",
      category: "Science",
      isFree: true,
    },
    // MIT OpenCourseWare
    {
      id: "mit-intro-cs",
      title: "Introduction to Computer Science",
      description: "MIT's famous intro to CS using Python - 6.0001",
      provider: "MIT OpenCourseWare",
      url: "https://ocw.mit.edu/courses/6-0001-introduction-to-computer-science-and-programming-in-python-fall-2016/",
      imageUrl: "https://ocw.mit.edu/static_shared/images/ocw_logo_orange.png",
      level: "Beginner",
      rating: 4.9,
      students: 2100000,
      duration: "50 hours",
      category: "Computer Science",
      isFree: true,
    },
    {
      id: "mit-linear-algebra",
      title: "Linear Algebra",
      description: "MIT's linear algebra course - 18.06SC",
      provider: "MIT OpenCourseWare",
      url: "https://ocw.mit.edu/courses/18-06sc-linear-algebra-fall-2011/",
      imageUrl: "https://ocw.mit.edu/static_shared/images/ocw_logo_orange.png",
      level: "Intermediate",
      rating: 4.9,
      students: 980000,
      duration: "70 hours",
      category: "Mathematics",
      isFree: true,
    },
    {
      id: "mit-algorithms",
      title: "Introduction to Algorithms",
      description: "MIT's comprehensive algorithms course - 6.006",
      provider: "MIT OpenCourseWare",
      url: "https://ocw.mit.edu/courses/6-006-introduction-to-algorithms-spring-2020/",
      imageUrl: "https://ocw.mit.edu/static_shared/images/ocw_logo_orange.png",
      level: "Advanced",
      rating: 4.8,
      students: 750000,
      duration: "80 hours",
      category: "Computer Science",
      isFree: true,
    },
    // Codecademy free courses
    {
      id: "codecademy-html",
      title: "Learn HTML",
      description: "Build the structure of web pages using HTML elements",
      provider: "Codecademy",
      url: "https://www.codecademy.com/learn/learn-html",
      imageUrl: "https://www.codecademy.com/resources/blog/wp-content/uploads/2022/12/what-is-html.png",
      level: "Beginner",
      rating: 4.6,
      students: 890000,
      duration: "9 hours",
      category: "Web Development",
      isFree: true,
    },
    {
      id: "codecademy-css",
      title: "Learn CSS",
      description: "Style web pages using CSS selectors and properties",
      provider: "Codecademy",
      url: "https://www.codecademy.com/learn/learn-css",
      imageUrl: "https://www.codecademy.com/resources/blog/wp-content/uploads/2022/01/CSS-1.png",
      level: "Beginner",
      rating: 4.5,
      students: 780000,
      duration: "10 hours",
      category: "Web Development",
      isFree: true,
    },
    {
      id: "codecademy-sql",
      title: "Learn SQL",
      description: "Master SQL for database querying and management",
      provider: "Codecademy",
      url: "https://www.codecademy.com/learn/learn-sql",
      imageUrl: "https://www.codecademy.com/resources/blog/wp-content/uploads/2022/11/What-is-SQL.png",
      level: "Beginner",
      rating: 4.7,
      students: 650000,
      duration: "8 hours",
      category: "Database",
      isFree: true,
    },
    // edX free courses
    {
      id: "harvard-cs50",
      title: "CS50: Introduction to Computer Science",
      description: "Harvard's legendary intro CS course",
      provider: "Harvard (edX)",
      url: "https://www.edx.org/course/introduction-computer-science-harvardx-cs50x",
      imageUrl: "https://prod-discovery.edx-cdn.org/media/course/image/da1b2400-322b-459b-97b0-0c557f05d017.png",
      level: "Beginner",
      rating: 4.9,
      students: 3500000,
      duration: "100 hours",
      category: "Computer Science",
      isFree: true,
    },
    {
      id: "ibm-data-science",
      title: "Data Science Fundamentals",
      description: "IBM's introduction to data science methodology",
      provider: "IBM (edX)",
      url: "https://www.edx.org/course/data-science-methodology",
      imageUrl: "https://www.edx.org/sites/default/files/course/image/promoted/ibm-data-science.jpg",
      level: "Beginner",
      rating: 4.5,
      students: 280000,
      duration: "20 hours",
      category: "Data Science",
      isFree: true,
    },
  ]

  // Simulate adding some random variation to student counts (real-time effect)
  return courses.map(course => ({
    ...course,
    students: course.students ? course.students + Math.floor(Math.random() * 100) : undefined
  }))
}

export function useFreeCourses() {
  const [courses, setCourses] = useState<Course[]>([])
  const [enrolledCourseIds, setEnrolledCourseIds] = useState<string[]>([])
  const [courseProgress, setCourseProgress] = useState<Record<string, number>>({})
  const [isLoading, setIsLoading] = useState(true)
  const [error, setError] = useState<string | null>(null)
  const [lastUpdated, setLastUpdated] = useState<Date | null>(null)

  // Load enrolled courses and progress from localStorage
  useEffect(() => {
    try {
      const enrolledKey = getEnrolledKey()
      const progressKey = getProgressKey()
      const storedEnrolled = localStorage.getItem(enrolledKey)
      const storedProgress = localStorage.getItem(progressKey)
      
      if (storedEnrolled) {
        setEnrolledCourseIds(JSON.parse(storedEnrolled))
      } else {
        setEnrolledCourseIds([]) // Reset for new user
      }
      if (storedProgress) {
        setCourseProgress(JSON.parse(storedProgress))
      } else {
        setCourseProgress({}) // Reset for new user
      }
    } catch (error) {
      console.error("Error loading course data:", error)
    }
  }, [])

  // Fetch courses
  const fetchCourses = useCallback(async () => {
    setIsLoading(true)
    setError(null)
    
    try {
      const fetchedCourses = await fetchFreeCourses()
      setCourses(fetchedCourses)
      setLastUpdated(new Date())
    } catch (err) {
      setError("Failed to fetch courses. Please try again.")
      console.error("Error fetching courses:", err)
    } finally {
      setIsLoading(false)
    }
  }, [])

  // Initial fetch
  useEffect(() => {
    fetchCourses()
  }, [fetchCourses])

  // Auto-refresh every 5 minutes (simulating real-time updates)
  useEffect(() => {
    const interval = setInterval(fetchCourses, 5 * 60 * 1000)
    return () => clearInterval(interval)
  }, [fetchCourses])

  // Enroll in a course
  const enrollCourse = useCallback((courseId: string) => {
    setEnrolledCourseIds(prev => {
      if (prev.includes(courseId)) return prev
      const updated = [...prev, courseId]
      const enrolledKey = getEnrolledKey()
      localStorage.setItem(enrolledKey, JSON.stringify(updated))
      return updated
    })
    
    // Initialize progress for new enrollment
    setCourseProgress(prev => {
      if (prev[courseId] !== undefined) return prev
      const updated = { ...prev, [courseId]: 0 }
      const progressKey = getProgressKey()
      localStorage.setItem(progressKey, JSON.stringify(updated))
      return updated
    })
  }, [])

  // Unenroll from a course
  const unenrollCourse = useCallback((courseId: string) => {
    setEnrolledCourseIds(prev => {
      const updated = prev.filter(id => id !== courseId)
      const enrolledKey = getEnrolledKey()
      localStorage.setItem(enrolledKey, JSON.stringify(updated))
      return updated
    })
  }, [])

  // Update course progress
  const updateProgress = useCallback((courseId: string, progress: number) => {
    setCourseProgress(prev => {
      const updated = { ...prev, [courseId]: Math.min(100, Math.max(0, progress)) }
      const progressKey = getProgressKey()
      localStorage.setItem(progressKey, JSON.stringify(updated))
      return updated
    })
  }, [])

  // Get enrolled courses with progress
  const enrolledCourses = courses
    .filter(course => enrolledCourseIds.includes(course.id))
    .map(course => ({
      ...course,
      progress: courseProgress[course.id] || 0
    }))

  // Get categories
  const categories = [...new Set(courses.map(c => c.category))]

  // Get providers
  const providers = [...new Set(courses.map(c => c.provider))]

  return {
    courses,
    enrolledCourses,
    enrolledCourseIds,
    courseProgress,
    categories,
    providers,
    isLoading,
    error,
    lastUpdated,
    fetchCourses,
    enrollCourse,
    unenrollCourse,
    updateProgress,
    isEnrolled: (courseId: string) => enrolledCourseIds.includes(courseId),
  }
}
